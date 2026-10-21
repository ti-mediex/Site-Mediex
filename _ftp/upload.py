# -*- coding: utf-8 -*-
"""Sobe alteracoes da pasta local ./site para o FTP.

Uso:
  python _ftp/upload.py                  -> mostra o que mudou (DRY-RUN, nao envia)
  python _ftp/upload.py --go             -> envia os arquivos alterados/novos
  python _ftp/upload.py --go index.html  -> envia so os caminhos informados
"""
import os
import sys

from ftp_common import (LOCAL_DIR, connect, encoding_utf8, file_sha, is_ignored,
                        list_dir, load_config, load_manifest, save_manifest)


def walk_local():
    out = []
    for dirpath, dirnames, filenames in os.walk(LOCAL_DIR):
        rel_dir = os.path.relpath(dirpath, LOCAL_DIR).replace("\\", "/")
        rel_dir = "" if rel_dir == "." else rel_dir
        dirnames[:] = [d for d in dirnames
                       if not is_ignored((rel_dir + "/" + d).lstrip("/"), True)]
        for name in filenames:
            rel = (rel_dir + "/" + name).lstrip("/")
            if is_ignored(rel, False):
                continue
            out.append(rel)
    return sorted(out)


def ensure_remote_dir(ftp, remote_root, rel_dir, cache):
    """Cria a arvore de diretorios remota se nao existir."""
    if not rel_dir or rel_dir in cache:
        return
    parts = rel_dir.split("/")
    for i in range(len(parts)):
        sub = "/".join(parts[:i + 1])
        if sub in cache:
            continue
        path = remote_root + "/" + sub
        try:
            ftp.cwd(path)
        except Exception:
            try:
                ftp.mkd(path)
                print("  [mkdir] %s" % sub)
            except Exception as exc:
                print("  [!] mkdir %s falhou: %s" % (sub, exc))
        cache.add(sub)


def main():
    go = "--go" in sys.argv
    alvos = [a.replace("\\", "/") for a in sys.argv[1:] if not a.startswith("--")]

    if not os.path.isdir(LOCAL_DIR):
        sys.exit("ERRO: pasta ./site nao existe. Rode o download.py primeiro.")

    cfg = load_config()
    manifest = load_manifest()
    locais = walk_local()

    if alvos:
        pendentes = [r for r in locais if r in alvos]
        faltando = [a for a in alvos if a not in locais]
        for f in faltando:
            print("[!] nao encontrado em ./site: %s" % f)
    else:
        pendentes = []
        for rel in locais:
            caminho = os.path.join(LOCAL_DIR, rel.replace("/", os.sep))
            size = os.path.getsize(caminho)
            antigo = manifest.get(rel)
            if antigo is None:
                pendentes.append(rel)          # arquivo novo
            elif antigo.get("size") != size:
                pendentes.append(rel)          # tamanho mudou
            elif antigo.get("sha") and antigo["sha"] != file_sha(caminho):
                pendentes.append(rel)          # mesmo tamanho, conteudo diferente

    if not pendentes:
        print("Nada para enviar -- tudo igual ao que foi baixado.")
        return

    print("=== %d arquivo(s) a enviar ===" % len(pendentes))
    for rel in pendentes:
        marca = "NOVO " if rel not in manifest else "ALTER"
        size = os.path.getsize(os.path.join(LOCAL_DIR, rel.replace("/", os.sep)))
        print("  [%s] %s (%d bytes)" % (marca, rel, size))

    if not go:
        print("\nDRY-RUN. Para enviar de verdade rode:  python _ftp/upload.py --go")
        return

    ftp = connect(cfg)
    encoding_utf8(ftp)
    remote_root = cfg["remote_dir"].rstrip("/")
    cache = set()
    enviados = falhas = 0

    for rel in pendentes:
        local_path = os.path.join(LOCAL_DIR, rel.replace("/", os.sep))
        rel_dir = os.path.dirname(rel)
        ensure_remote_dir(ftp, remote_root, rel_dir, cache)
        erro = None
        for tentativa in range(3):
            try:
                with open(local_path, "rb") as fh:
                    ftp.storbinary("STOR " + remote_root + "/" + rel, fh)
                erro = None
                break
            except Exception as exc:
                erro = exc
                # conexao caiu (timeout, limite do servidor): reconecta e tenta de novo
                try:
                    ftp.close()
                except Exception:
                    pass
                import time
                time.sleep(2 * (tentativa + 1))
                try:
                    ftp = connect(cfg)
                    encoding_utf8(ftp)
                    cache = set()
                except Exception as exc2:
                    erro = exc2
        if erro is None:
            manifest[rel] = {"size": os.path.getsize(local_path), "modify": "",
                             "sha": file_sha(local_path)}
            enviados += 1
            print("  [enviado] %s" % rel)
            if enviados % 100 == 0:
                save_manifest(manifest)   # progresso salvo: uma queda nao perde o que ja subiu
        else:
            falhas += 1
            print("  [ERRO] %s -> %s" % (rel, erro))

    save_manifest(manifest)
    try:
        ftp.quit()
    except Exception:
        ftp.close()

    print("\n=== RESUMO ===")
    print("enviados: %d | falhas: %d" % (enviados, falhas))


if __name__ == "__main__":
    main()
