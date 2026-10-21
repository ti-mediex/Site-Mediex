# -*- coding: utf-8 -*-
"""Baixa o site inteiro do FTP para ./site usando varias conexoes em paralelo.

Uso:
  python download.py             -> baixa tudo (pula arquivos ja iguais)
  python download.py --force     -> rebaixa tudo
  python download.py --list      -> so mapeia a estrutura remota
  python download.py --jobs 12   -> muda o numero de conexoes (padrao 8)
"""
import os
import queue
import sys
import threading
import time

from ftp_common import (LOCAL_DIR, connect, encoding_utf8, is_ignored,
                        list_dir, load_config, save_manifest)

_local = threading.local()
CFG = None
PRINT_LOCK = threading.Lock()


def log(msg):
    with PRINT_LOCK:
        print(msg, flush=True)


def get_ftp():
    """Uma conexao FTP por thread, reconectando se cair."""
    ftp = getattr(_local, "ftp", None)
    if ftp is not None:
        try:
            ftp.voidcmd("NOOP")
            return ftp
        except Exception:
            try:
                ftp.close()
            except Exception:
                pass
    for tentativa in range(3):
        try:
            ftp = connect(CFG)
            encoding_utf8(ftp)
            _local.ftp = ftp
            return ftp
        except Exception as exc:
            if tentativa == 2:
                raise
            time.sleep(2)


def close_ftp():
    ftp = getattr(_local, "ftp", None)
    if ftp is not None:
        try:
            ftp.quit()
        except Exception:
            try:
                ftp.close()
            except Exception:
                pass
        _local.ftp = None


# ---------------------------------------------------------------- mapeamento
def mapear(remote_root, jobs):
    """BFS paralelo: devolve lista de (rel_path, size, modify)."""
    pendentes = queue.Queue()
    pendentes.put("")
    encontrados = []
    lock = threading.Lock()
    ativos = threading.Semaphore(0)
    contador = {"dirs": 0}
    restantes = [1]  # diretorios ainda nao processados

    def worker():
        while True:
            try:
                rel = pendentes.get(timeout=1)
            except queue.Empty:
                with lock:
                    if restantes[0] <= 0:
                        return
                continue
            try:
                ftp = get_ftp()
                path = remote_root if not rel else remote_root + "/" + rel
                dirs, files = list_dir(ftp, path)
                novos = []
                for name in dirs:
                    child = name if not rel else rel + "/" + name
                    if is_ignored(child, True):
                        continue
                    novos.append(child)
                with lock:
                    contador["dirs"] += 1
                    restantes[0] += len(novos)
                    for name, size, modify in files:
                        child = name if not rel else rel + "/" + name
                        if not is_ignored(child, False):
                            encontrados.append((child, size, modify))
                    if contador["dirs"] % 25 == 0:
                        log("    ... %d pastas mapeadas, %d arquivos"
                            % (contador["dirs"], len(encontrados)))
                for n in novos:
                    pendentes.put(n)
            except Exception as exc:
                log("    [!] falha ao listar '%s': %s" % (rel, exc))
            finally:
                with lock:
                    restantes[0] -= 1
                pendentes.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return encontrados


# ------------------------------------------------------------------ download
def baixar(entries, remote_root, jobs, force):
    fila = queue.Queue()
    for e in sorted(entries):
        fila.put(e)

    total = len(entries)
    stats = {"ok": 0, "skip": 0, "erro": 0, "feitos": 0}
    manifest = {}
    lock = threading.Lock()

    def worker():
        while True:
            try:
                rel, size, modify = fila.get_nowait()
            except queue.Empty:
                return
            local_path = os.path.join(LOCAL_DIR, rel.replace("/", os.sep))
            try:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                if (not force and os.path.exists(local_path)
                        and os.path.getsize(local_path) == size):
                    with lock:
                        manifest[rel] = {"size": size, "modify": modify}
                        stats["skip"] += 1
                        stats["feitos"] += 1
                    continue

                ftp = get_ftp()
                tmp = local_path + ".part"
                with open(tmp, "wb") as fh:
                    ftp.retrbinary("RETR " + remote_root + "/" + rel, fh.write)
                if os.path.exists(local_path):
                    os.remove(local_path)
                os.rename(tmp, local_path)

                with lock:
                    manifest[rel] = {"size": size, "modify": modify}
                    stats["ok"] += 1
                    stats["feitos"] += 1
                    if stats["feitos"] % 50 == 0:
                        log("    ... %d/%d arquivos" % (stats["feitos"], total))
            except Exception as exc:
                with lock:
                    stats["erro"] += 1
                    stats["feitos"] += 1
                log("    [ERRO] %s -> %s" % (rel, exc))
                for p in (local_path + ".part",):
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except Exception:
                            pass
            finally:
                fila.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return manifest, stats


def main():
    global CFG
    force = "--force" in sys.argv
    only_list = "--list" in sys.argv
    jobs = 8
    if "--jobs" in sys.argv:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1])

    CFG = load_config()
    remote_root = CFG["remote_dir"].rstrip("/")
    t0 = time.time()

    log("[..] mapeando %s com %d conexoes ..." % (remote_root, jobs))
    entries = mapear(remote_root, jobs)
    mb = sum(e[1] for e in entries) / 1048576.0
    log("[ok] %d arquivos, %.2f MB  (%.1fs)" % (len(entries), mb, time.time() - t0))

    if only_list:
        for rel, size, _ in sorted(entries):
            print("%10d  %s" % (size, rel))
        return

    log("[..] baixando com %d conexoes ..." % jobs)
    manifest, stats = baixar(entries, remote_root, jobs, force)
    save_manifest(manifest)

    log("\n=== RESUMO ===")
    log("baixados: %d | ja existiam: %d | erros: %d" % (stats["ok"], stats["skip"], stats["erro"]))
    log("tempo total: %.1fs" % (time.time() - t0))
    log("pasta local: %s" % LOCAL_DIR)


if __name__ == "__main__":
    main()
