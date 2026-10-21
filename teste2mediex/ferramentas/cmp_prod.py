# -*- coding: utf-8 -*-
"""Compara o build local ./site com o que esta no ar em mediex.com.br.

Uso:
  python teste2mediex/ferramentas/cmp_prod.py              -> compara todos os .html
  python teste2mediex/ferramentas/cmp_prod.py pcmso-recife -> so os caminhos informados

Por que existe: o HTML servido NUNCA bate byte a byte com o local, porque o
Cloudflare injeta tres coisas que nao estao no build. Sem neutralizar as tres,
toda pagina aparece como "diferente" e a comparacao nao serve para nada:

  1. beacon do Cloudflare Insights (<script type="module" ...cloudflareinsights...>)
     mais o helper inline que vem junto, colados antes de </body>  (~1305 bytes)
  2. bloco de "JavaScript Detections" (__CF$cv$params) — o token muda a CADA
     request, entao a mesma pagina difere de si mesma entre duas buscas
  3. ofuscacao de e-mail: mailto: -> /cdn-cgi/l/email-protection#<hex>, e o texto
     virando <span class="__cf_email__"> OU <a class="__cf_email__"> (as duas formas
     aparecem no site; cobrir so o span deixa paginas como /exames-lp falsamente
     diferentes)

Precisa de UA de navegador: com UA de curl o Cloudflare serve outra coisa.
"""
import os, re, sys, hashlib, urllib.request, concurrent.futures as cf

BS = chr(92)
BASE = 'https://mediex.com.br'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'site')
RAIZ = os.path.normpath(RAIZ)
# 404 por desenho; /exames tem Redirect 301 para a home no .htaccess
PULA = {'404.html', '_not-found.html', 'exames.html'}


def tira_cloudflare(t):
    i = t.find('<script type="module" src="https://static.cloudflareinsights.com')
    if i > 0:
        j = t.find('</body>', i)
        if j > 0:
            t = t[:i] + t[j:]
    while True:
        k = t.find('__CF$cv$params')
        if k < 0:
            break
        ini = t.rfind('<script', 0, k)
        fim = t.find('</script>', k)
        if ini < 0 or fim < 0:
            break
        t = t[:ini] + t[fim + len('</script>'):]
    return t


def normaliza(t):
    t = tira_cloudflare(t)
    t = re.sub(r'<script[^>]*email-decode[^>]*>\s*</script>', '', t)
    # o e-mail tem DUAS formas no build: ora <a href="mailto:...">, ora texto puro.
    # O Cloudflare troca a primeira e ENVOLVE a segunda num <a> novo, entao os dois
    # lados viram o mesmo marcador em vez de tentar casar atributo por atributo.
    t = re.sub(r'<(span|a)\b[^>]*(?:__cf_email__|email-protection)[^>]*>.*?</\1>', 'MAIL', t, flags=re.S)
    t = re.sub(r'<a\b[^>]*mailto:[^>]*>.*?</a>', 'MAIL', t, flags=re.S)
    t = re.sub(r'data-cfemail="[0-9a-f]*"', '', t)
    t = re.sub(r'/cdn-cgi/l/email-protection(#[0-9a-f]*)?', 'MAIL', t)
    t = re.sub(r'mailto:', '', t)
    t = re.sub(r'[A-Za-z0-9._%+-]+(@|%40|&#64;)mediex\.com\.br', 'MAIL', t)
    t = re.sub(r'\[email(&#160;|&nbsp;|\s)*protected\]', 'MAIL', t)
    t = re.sub(r'(?:MAIL\s*){2,}', 'MAIL', t)
    t = re.sub(r'\s+', ' ', t)
    return hashlib.sha1(t.encode('utf-8', 'replace')).hexdigest()


def rota(rel):
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('/index.html')]
    return '/' + rel[:-len('.html')]


def lista(alvos):
    out = []
    for b, ds, fs in os.walk(RAIZ):
        for f in fs:
            if not f.endswith('.html'):
                continue
            p = os.path.join(b, f)
            rel = os.path.relpath(p, RAIZ).replace(BS, '/')
            if rel in PULA:
                continue
            if alvos and not any(a.strip('/') in (rel, rel[:-5]) for a in alvos):
                continue
            out.append((rel, p))
    return sorted(out)


def checa(item):
    rel, p = item
    try:
        req = urllib.request.Request(BASE + rota(rel),
                                     headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
        prod = urllib.request.urlopen(req, timeout=45).read().decode('utf-8', 'replace')
    except Exception as exc:
        return (rel, 'ERRO', str(exc)[:60])
    loc = open(p, encoding='utf-8', errors='replace').read()
    igual = normaliza(loc) == normaliza(prod)
    return (rel, 'IGUAL' if igual else 'DIFERE', '%d/%d bytes' % (len(loc), len(prod)))


def main():
    alvos = [a for a in sys.argv[1:] if not a.startswith('--')]
    itens = lista(alvos)
    if not itens:
        sys.exit('nada para comparar')
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(checa, itens))
    ruins = [r for r in res if r[1] != 'IGUAL']
    print('comparadas %d | IGUAIS %d | problemas %d' % (len(res), len(res) - len(ruins), len(ruins)))
    for r in ruins:
        print('   %-7s %-55s %s' % (r[1], r[0], r[2]))
    return 1 if ruins else 0


if __name__ == '__main__':
    sys.exit(main())
