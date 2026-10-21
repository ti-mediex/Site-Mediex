# -*- coding: utf-8 -*-
"""Servidor local da COPIA DE TESTE (teste2mediex) - nao toca no ./site original.

Uso:
  python serve.py            -> http://localhost:8081
  python serve.py 3001       -> http://localhost:3001

Resolve rotas sem extensao do jeito que o Next.js exporta:
  /pcmso-recife  ->  site/pcmso-recife.html  ou  site/pcmso-recife/index.html

Imita a producao (mediex.com.br) para o teste ser fiel:
  - mesmos headers de seguranca do .htaccess (CSP sem upgrade-insecure-requests,
    que quebraria o http://localhost; sem HSTS, que nao se aplica a http)
  - /exames -> 301 para / (regra do .htaccess)
  - prefetch de segmentos do Next: __next.<seg>.<sub>.txt -> __next.<seg>/<sub>.txt
    (a regra nova do .htaccess desta copia)
"""
import http.server
import mimetypes
import os
import posixpath
import re
import socketserver
import sys
import urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com "
       "https://www.googletagmanager.com https://googleads.g.doubleclick.net https://elfsightcdn.com "
       "https://static.elfsight.com https://*.clarity.ms https://d335luupugsy2.cloudfront.net "
       "https://d1sag09wwfbul8.cloudfront.net; "
       "style-src 'self' 'unsafe-inline' https://d335luupugsy2.cloudfront.net; "
       "img-src 'self' data: blob: https:; "
       "font-src 'self' data: https://d335luupugsy2.cloudfront.net https://dk9suync0k2va.cloudfront.net; "
       "connect-src 'self' "
       "https://cloudflareinsights.com https://*.cloudflareinsights.com https://brasilapi.com.br "
       "https://pisctwabgnfthixgyhco.supabase.co https://*.elfsight.com https://*.elfsightcdn.com "
       "https://api.featurable.com https://www.googletagmanager.com https://*.google-analytics.com "
       "https://*.analytics.google.com https://www.google.com https://google.com https://www.google.com.br "
       "https://google.com.br https://*.doubleclick.net https://www.googleadservices.com https://*.clarity.ms "
       "https://c.bing.com https://d335luupugsy2.cloudfront.net https://d1sag09wwfbul8.cloudfront.net "
       "https://*.rdstation.com.br https://event-harbor.rdstation.com; "
       "frame-src 'self' https://www.google.com https://www.youtube.com "
       "https://www.youtube-nocookie.com https://td.doubleclick.net https://www.googletagmanager.com; "
       "media-src 'self'; object-src 'none'; base-uri 'self'; "
       "form-action 'self' https://*.rdstation.com.br; frame-ancestors 'self'")

HEADERS_PROD = {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
    "Content-Security-Policy": CSP,
    "Cross-Origin-Opener-Policy": "same-origin",
}

SEGMENTO = re.compile(r"^(__next\.[^./]+)((?:\.[^./]+)+)\.txt$")

mimetypes.add_type("text/html; charset=utf-8", ".html")
mimetypes.add_type("text/css; charset=utf-8", ".css")
mimetypes.add_type("application/javascript; charset=utf-8", ".js")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json; charset=utf-8", ".json")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        path = urllib.parse.urlsplit(path).path
        path = urllib.parse.unquote(path, errors="surrogatepass")
        path = posixpath.normpath(path).lstrip("/")

        # bloqueia tentativa de sair da pasta site/
        partes = [p for p in path.split("/") if p not in ("", ".", "..")]
        alvo = os.path.join(ROOT, *partes)

        if os.path.isdir(alvo):
            idx = os.path.join(alvo, "index.html")
            if os.path.exists(idx):
                return idx
            if os.path.exists(alvo + ".html"):
                return alvo + ".html"
        if os.path.exists(alvo) and os.path.isfile(alvo):
            return alvo
        # prefetch de segmento do Next: __next.a.b.c.txt -> __next.a/b/c.txt
        if partes:
            m = SEGMENTO.match(partes[-1])
            if m:
                sub = m.group(2).lstrip(".").split(".")
                cand = os.path.join(ROOT, *partes[:-1], m.group(1), *sub[:-1], sub[-1] + ".txt")
                if os.path.isfile(cand):
                    return cand
        # rota sem extensao -> tenta .html
        if not os.path.splitext(alvo)[1]:
            if os.path.exists(alvo + ".html"):
                return alvo + ".html"
            idx = os.path.join(alvo, "index.html")
            if os.path.exists(idx):
                return idx
        return alvo

    def send_head(self):
        if urllib.parse.urlsplit(self.path).path.rstrip("/") == "/exames":
            self.send_response(301)
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        caminho = self.translate_path(self.path)
        if not os.path.exists(caminho):
            for pag404 in (os.path.join(ROOT, "404.html"),
                           os.path.join(ROOT, "_not-found", "index.html"),
                           os.path.join(ROOT, "_not-found.html")):
                if os.path.exists(pag404):
                    corpo = open(pag404, "rb").read()
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(corpo)))
                    self.end_headers()
                    return __import__("io").BytesIO(corpo)
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        for nome, valor in HEADERS_PROD.items():
            self.send_header(nome, valor)
        super().end_headers()

    def log_message(self, fmt, *args):
        codigo = args[1] if len(args) > 1 else ""
        if str(codigo).startswith(("4", "5")):
            sys.stderr.write("  %s %s\n" % (codigo, args[0]))


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    if not os.path.isdir(ROOT):
        sys.exit("ERRO: pasta ./site nao existe. Rode _ftp/download.py primeiro.")
    with Servidor(("127.0.0.1", porta), Handler) as httpd:
        print("TESTE2MEDIEX (copia de teste) - servindo %s" % ROOT)
        print("  -> http://localhost:%d" % porta)
        print("Ctrl+C para parar.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nparado.")


if __name__ == "__main__":
    main()
