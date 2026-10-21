# -*- coding: utf-8 -*-
"""Conexao FTP/FTPS compartilhada + utilitarios de manifest."""
import ftplib
import json
import os
import ssl
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
CONFIG_PATH = os.path.join(BASE, "config.json")
MANIFEST_PATH = os.path.join(BASE, "manifest.json")
LOCAL_DIR = os.path.join(ROOT, "site")

# Nao baixar/subir esses caminhos
IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".well-known/acme-challenge"}
IGNORE_FILES = {".DS_Store", "Thumbs.db", "error_log", ".ftpquota"}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.exit("ERRO: falta o arquivo _ftp/config.json (copie de config.example.json)")
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    for key in ("host", "user", "password"):
        if not cfg.get(key):
            sys.exit("ERRO: campo '%s' vazio em config.json" % key)
    cfg.setdefault("port", 21)
    cfg.setdefault("remote_dir", "/public_html")
    cfg.setdefault("use_tls", True)
    cfg.setdefault("passive", True)
    return cfg


def connect(cfg):
    """Tenta FTPS explicito; se o servidor nao suportar, cai para FTP simples."""
    host, port = cfg["host"], int(cfg["port"])
    user, password = cfg["user"], cfg["password"]

    if cfg["use_tls"]:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ftp = ftplib.FTP_TLS(context=ctx, timeout=30)
            ftp.connect(host, port)
            ftp.login(user, password)
            ftp.prot_p()
            ftp.set_pasv(cfg["passive"])
            print("[ok] conectado com FTPS (TLS) em %s:%s" % (host, port))
            return ftp
        except Exception as exc:
            print("[aviso] FTPS falhou (%s) -- tentando FTP simples" % exc)

    ftp = ftplib.FTP(timeout=30)
    ftp.connect(host, port)
    ftp.login(user, password)
    ftp.set_pasv(cfg["passive"])
    print("[ok] conectado com FTP simples em %s:%s" % (host, port))
    return ftp


def encoding_utf8(ftp):
    try:
        ftp.sendcmd("OPTS UTF8 ON")
        ftp.encoding = "utf-8"
    except Exception:
        pass


def list_dir(ftp, path):
    """Retorna (dirs, files[(nome, tamanho, modify)]) usando MLSD, com fallback."""
    dirs, files = [], []
    try:
        for name, facts in ftp.mlsd(path, facts=["type", "size", "modify"]):
            if name in (".", ".."):
                continue
            kind = facts.get("type")
            if kind == "dir":
                dirs.append(name)
            elif kind == "file":
                files.append((name, int(facts.get("size", 0)), facts.get("modify", "")))
        return dirs, files
    except Exception:
        pass

    lines = []
    ftp.cwd(path)
    ftp.retrlines("LIST", lines.append)
    for line in lines:
        parts = line.split(None, 8)
        if len(parts) < 9:
            continue
        perms, name = parts[0], parts[8]
        if name in (".", ".."):
            continue
        if perms.startswith("d"):
            dirs.append(name)
        elif perms.startswith("-"):
            try:
                size = int(parts[4])
            except ValueError:
                size = 0
            files.append((name, size, ""))
    return dirs, files


def is_ignored(rel_path, is_dir):
    parts = rel_path.replace("\\", "/").split("/")
    base = parts[-1]
    if is_dir:
        return base in IGNORE_DIRS
    if base in IGNORE_FILES:
        return True
    return any(p in IGNORE_DIRS for p in parts[:-1])


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_manifest(data):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False, sort_keys=True)


def file_sha(path):
    import hashlib
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
