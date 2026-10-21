# -*- coding: utf-8 -*-
"""Servidor local para o site estatico (Next.js export) da pasta ./site

Uso:
  python serve.py            -> http://localhost:8080
  python serve.py 3000       -> http://localhost:3000

Resolve rotas sem extensao do jeito que o Next.js exporta:
  /pcmso-recife  ->  site/pcmso-recife.html  ou  site/pcmso-recife/index.html
"""
import http.server
import mimetypes
import os
import posixpath
import socketserver
import sys
import urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

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
        # rota sem extensao -> tenta .html
        if not os.path.splitext(alvo)[1]:
            if os.path.exists(alvo + ".html"):
                return alvo + ".html"
            idx = os.path.join(alvo, "index.html")
            if os.path.exists(idx):
                return idx
        return alvo

    def send_head(self):
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
        super().end_headers()

    def log_message(self, fmt, *args):
        codigo = args[1] if len(args) > 1 else ""
        if str(codigo).startswith(("4", "5")):
            sys.stderr.write("  %s %s\n" % (codigo, args[0]))


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    if not os.path.isdir(ROOT):
        sys.exit("ERRO: pasta ./site nao existe. Rode _ftp/download.py primeiro.")
    with Servidor(("127.0.0.1", porta), Handler) as httpd:
        print("Servindo %s" % ROOT)
        print("  -> http://localhost:%d" % porta)
        print("Ctrl+C para parar.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nparado.")


if __name__ == "__main__":
    main()
