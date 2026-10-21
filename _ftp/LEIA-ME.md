# Fluxo FTP - Site MEDIEX

Servidor: `ftp.mediex.com.br` (Pure-FTPd / cPanel, **FTPS explicito na porta 21**)
Raiz do site: `/public_html` (site Next.js exportado estatico)

## Estrutura

```
SITE MEDIEX/
  site/            <- copia local do /public_html (edite AQUI)
  _ftp/
    config.json         <- credenciais (NAO compartilhar)
    ftp_common.py       <- conexao FTPS + utilitarios
    download.py         <- baixa do servidor
    upload.py           <- envia para o servidor
    manifest.json       <- estado do que foi baixado (detecta alteracoes)
```

## Comandos

Rodar sempre de dentro da pasta `_ftp`.

### Baixar
```bash
python download.py            # baixa tudo (pula arquivos ja iguais)
python download.py --force    # rebaixa tudo do zero
python download.py --list     # so lista a estrutura remota
```

### Enviar
```bash
python upload.py                    # DRY-RUN: mostra o que mudou, nao envia
python upload.py --go               # envia tudo que mudou
python upload.py --go index.html    # envia so os arquivos informados
```

O `upload.py` compara com o `manifest.json` gerado no download, entao ele so
sobe o que voce realmente alterou. O modo sem `--go` e sempre seguro.

## Cuidados

- O usuario FTP tem acesso a **raiz da conta cPanel**, nao so ao public_html.
  Os scripts estao travados em `/public_html` pelo campo `remote_dir`.
- Existe um `/public_html_old` no servidor (versao anterior do site) - nao mexer.
- O `config.json` guarda a senha em texto puro. Nao versionar nem enviar
  para lugar nenhum.
