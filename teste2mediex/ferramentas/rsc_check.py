import json, re, sys

PUSH = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')


def stream_from_html(path):
    h = open(path, encoding='utf-8').read()
    return ''.join(json.loads(m.group(1)) for m in PUSH.finditer(h))


def rows(data):
    """Percorre o stream RSC (bytes). Linha T = id:T<hex bytes>,<conteudo>; demais = id:<json>\\n."""
    b = data if isinstance(data, bytes) else data.encode('utf-8')
    i, out = 0, []
    while i < len(b):
        j = b.index(b':', i)
        rid = b[i:j].decode('utf-8', 'replace')
        k = j + 1
        if b[k:k + 1] == b'T':
            c = b.index(b',', k)
            n = int(b[k + 1:c], 16)
            out.append((rid, 'T', c + 1, c + 1 + n, n))
            i = c + 1 + n
        else:
            e = b.find(b'\n', k)
            e = len(b) if e < 0 else e
            out.append((rid, 'J', k, e, None))
            i = e + 1
    return b, out


def check(label, data):
    try:
        b, rs = rows(data)
    except Exception as ex:
        print(label, 'FALHOU AO PARSEAR:', repr(ex)[:160])
        return
    ruins = []
    for r in rs:
        if r[1] == 'J':
            linha = b[r[2]:r[3]]
            ok_ids = re.fullmatch(rb'[0-9a-f]+', r[0].encode()) is not None
            if not ok_ids:
                ruins.append(r)
    ts = [r for r in rs if r[1] == 'T']
    print('%-9s linhas=%d blocosT=%d ids_invalidos=%d' % (label, len(rs), len(ts), len(ruins)))
    for r in ts:
        txt = b[r[2]:r[3]].decode('utf-8', 'replace')
        flags = [k for k in ('Solu', 'Medicina e Seg', 'could not be found', 'encontrada', 'reviewCount') if k in txt]
        if flags:
            print('   T id=%s declarado=%d contem=%s' % (r[0], r[4], flags))
    if ruins:
        r = ruins[0]
        print('   1a linha com id invalido: %r ... %r' % (r[0][:40], b[r[2]:r[2] + 60]))


if __name__ == '__main__':
    for label, path in zip(('ORIGINAL', 'TESTE2'), sys.argv[1:3]):
        data = stream_from_html(path) if path.endswith('.html') else open(path, 'rb').read()
        check(label, data)
