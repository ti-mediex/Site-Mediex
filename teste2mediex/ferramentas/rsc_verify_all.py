"""Confere, arquivo por arquivo, que o fluxo RSC da copia teste2mediex parseia sozinho
(com os proprios cabecalhos T) na MESMA sequencia de linhas (ids e tipos) do original."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from rsc_fix_tlen import ORIG, TEST, PUSH, rows


def stream(path):
    if path.endswith('.html'):
        h = open(path, encoding='utf-8').read()
        return ''.join(json.loads(m.group(1)) for m in PUSH.finditer(h)).encode('utf-8')
    return open(path, 'rb').read()


ok = ruins = pulados = 0
lista = []
for dp, dn, fn in os.walk(TEST):
    if os.sep + '_next' + os.sep in dp + os.sep:
        continue
    for f in fn:
        if not (f.endswith('.html') or f.endswith('.txt')):
            continue
        tp = os.path.join(dp, f)
        rel = os.path.relpath(tp, TEST)
        op = os.path.join(ORIG, rel)
        if not os.path.exists(op):
            continue
        ob, tb = stream(op), stream(tp)
        if not ob or b':' not in ob[:40]:
            pulados += 1
            continue
        try:
            a, b = rows(ob), rows(tb)
            igual = [(r[0], r[1]) for r in a] == [(r[0], r[1]) for r in b]
            # o fim de cada bloco T tem que cair exatamente no inicio da linha seguinte
        except Exception as ex:
            igual = False
        if igual:
            ok += 1
        else:
            ruins += 1
            lista.append(rel)
print('estrutura OK: %d | QUEBRADOS: %d | sem payload RSC (ignorados): %d' % (ok, ruins, pulados))
for r in lista[:20]:
    print('  quebrado:', r)
