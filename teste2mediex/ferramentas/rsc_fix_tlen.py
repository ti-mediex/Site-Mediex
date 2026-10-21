"""Recalcula o tamanho declarado dos blocos T do payload RSC (id:T<hex bytes>,<texto>)
na copia teste2mediex, depois de trocas de texto que mudaram o tamanho do conteudo.

Usa o arquivo equivalente do site ORIGINAL como mapa da estrutura (ordem e ids das linhas).
So mexe nos digitos hex dos cabecalhos T. Valida re-parseando o fluxo inteiro.

Uso:  python rsc_fix_tlen.py            -> dry-run (so relata)
      python rsc_fix_tlen.py --go       -> grava (com backup)
"""
import json, os, re, shutil, sys

BASE = r"C:\Users\iagoTi\Desktop\SITE MEDIEX"
ORIG = os.path.join(BASE, "site")
TEST = os.path.join(BASE, "teste2mediex", "site")
BACKUP = r"C:\Users\iagoTi\AppData\Local\Temp\claude\C--Users-iagoTi-Desktop-SITE-MEDIEX\573deb0b-32aa-46c8-bd14-5fe68cf71d64\scratchpad\backup_tlen"
PUSH = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
JANELA = 4000  # bytes de folga em volta do fim esperado de um bloco T


def rows(b):
    i, out = 0, []
    while i < len(b):
        j = b.index(b':', i)
        rid = b[i:j]
        k = j + 1
        if b[k:k + 1] == b'T':
            c = b.index(b',', k)
            n = int(b[k + 1:c], 16)
            out.append((rid, 'T', i, c + 1, c + 1 + n, n))
            i = c + 1 + n
        else:
            e = b.find(b'\n', k)
            e = len(b) if e < 0 else e
            out.append((rid, 'J', i, k, e, None))
            i = e + 1
    return out


def corrigir_stream(ob, mb):
    """ob/mb = bytes do fluxo original/modificado. Devolve lista de (hdr_antigo, hdr_novo)."""
    orows = rows(ob)
    edits, p = [], 0
    for idx, (rid, kind, h0, c0, c1, n) in enumerate(orows):
        if not mb.startswith(rid + b':', p):
            raise ValueError('linha %r nao comeca onde esperado (pos %d)' % (rid, p))
        if kind == 'J':
            e = mb.find(b'\n', p)
            p = len(mb) if e < 0 else e + 1
            continue
        k = p + len(rid) + 1
        c = mb.index(b',', k)
        old_hex = mb[k + 1:c]
        start = c + 1
        if idx + 1 < len(orows):
            nxt = orows[idx + 1]
            agulha = nxt[0] + b':' + ob[nxt[3]:nxt[3] + 24] if nxt[1] == 'J' else nxt[0] + b':T'
            alvo = start + n
            cands = [m.start() for m in re.finditer(re.escape(agulha), mb[max(start, alvo - JANELA):alvo + JANELA])]
            if not cands:
                raise ValueError('fim do bloco T %r nao encontrado' % rid)
            base = max(start, alvo - JANELA)
            fim = min((base + x for x in cands), key=lambda x: abs(x - alvo))
        else:
            fim = len(mb)
        novo = fim - start
        if novo != n or int(old_hex, 16) != novo:
            hdr_old = rid + b':T' + old_hex + b','
            hdr_new = rid + b':T' + format(novo, 'x').encode() + b','
            edits.append((hdr_old, hdr_new, n, novo))
        p = fim
    return edits


def validar(ob, fixed):
    a, b = rows(ob), rows(fixed)
    return [r[0] for r in a] == [r[0] for r in b] and [r[1] for r in a] == [r[1] for r in b]


def processar(rel, go):
    op, tp = os.path.join(ORIG, rel), os.path.join(TEST, rel)
    if rel.endswith('.html'):
        oh = open(op, encoding='utf-8').read()
        th = open(tp, encoding='utf-8').read()
        ob = ''.join(json.loads(m.group(1)) for m in PUSH.finditer(oh)).encode('utf-8')
        tl = list(PUSH.finditer(th))
        mb = ''.join(json.loads(m.group(1)) for m in tl).encode('utf-8')
    else:
        ob, mb = open(op, 'rb').read(), open(tp, 'rb').read()
    if not ob or b':T' not in ob:
        return None
    edits = corrigir_stream(ob, mb)
    if not edits:
        return 0
    fixed = mb
    for hdr_old, hdr_new, _, _ in edits:
        assert fixed.count(hdr_old) >= 1
        fixed = fixed.replace(hdr_old, hdr_new, 1)
    if not validar(ob, fixed):
        raise ValueError('estrutura diferente do original depois da correcao')
    if go:
        dst = os.path.join(BACKUP, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(tp, dst)
        if rel.endswith('.html'):
            novo = th
            for hdr_old, hdr_new, _, _ in edits:
                # cabecalho e ASCII puro: aparece literal dentro da string do push
                h_old, h_new = hdr_old.decode(), hdr_new.decode()
                if novo.count(h_old) != 1:
                    raise ValueError('cabecalho %s aparece %d vezes no html' % (h_old, novo.count(h_old)))
                novo = novo.replace(h_old, h_new, 1)
            open(tp, 'w', encoding='utf-8', newline='').write(novo)
        else:
            open(tp, 'wb').write(fixed)
    return len(edits)


def main():
    go = '--go' in sys.argv
    tot_arq = tot_blocos = 0
    erros = []
    for dp, dn, fn in os.walk(TEST):
        if os.sep + '_next' + os.sep in dp + os.sep:
            continue
        for f in fn:
            if not (f.endswith('.html') or f.endswith('.txt')):
                continue
            tp = os.path.join(dp, f)
            rel = os.path.relpath(tp, TEST)
            if not os.path.exists(os.path.join(ORIG, rel)):
                continue
            try:
                r = processar(rel, go)
            except Exception as ex:
                erros.append((rel, str(ex)[:150]))
                continue
            if r:
                tot_arq += 1
                tot_blocos += r
    print('%s: %d arquivos com blocos T corrigidos, %d blocos no total' % ('GRAVADO' if go else 'DRY-RUN', tot_arq, tot_blocos))
    print('erros: %d' % len(erros))
    for e in erros[:15]:
        print('  ', e)


if __name__ == '__main__':
    main()
