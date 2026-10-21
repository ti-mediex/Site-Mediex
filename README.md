# Site Mediex — mediex.com.br

Build estático do site da Mediex (clínica de medicina e segurança do trabalho em
Recife), servido por cPanel atrás do Cloudflare.

**Este repositório não é o código-fonte.** É o *output* exportado de um projeto
Next.js (App Router, Turbopack) ao qual não temos acesso. As correções são feitas
direto no build e publicadas por FTP. Se alguém algum dia rebuildar a partir do
projeto original, as edições feitas aqui se perdem.

## Estrutura

| Pasta | O que é |
|---|---|
| `site/` | O build que está no ar. É o que o `upload.py` publica. |
| `_ftp/` | Publicação por FTPS: `download.py`, `upload.py`, `manifest.json`. |
| `_backups/` | Backups datados de cada intervenção, com os respectivos LEIA-ME. |
| `teste2mediex/` | Servidor local que imita CSP, headers e regras da produção (porta 8081), mais as ferramentas. |
| `exemplos/` | Arquivos que não podem ser versionados com credenciais (ver abaixo). |
| `serve.py` | Servidor local simples para `site/`. |

## Publicar

```bash
python _ftp/upload.py                  # dry-run: mostra o que mudou
python _ftp/upload.py --go             # envia os alterados
python _ftp/upload.py --go index.html  # envia só os caminhos informados
```

O `.htaccess` sobe **sozinho** e se testa 500 na hora: ele tem centenas de
`Redirect 301` herdados do WordPress antigo, e um erro ali derruba o site todo.

## Armadilhas deste build

Editar HTML exportado do Next.js não é editar HTML. Antes de mexer:

- **Blocos T do payload RSC têm o tamanho em bytes no cabeçalho** (`id:T<hex>,<texto>`).
  Trocar texto dentro de um bloco T sem recalcular o hex quebra o site inteiro no
  navegador ("This page couldn't load"), mesmo com o HTML servido parecendo correto.
  Use `teste2mediex/ferramentas/rsc_fix_tlen.py` e valide com `rsc_verify_all.py`.
- **O React re-renderiza a partir do payload `__next_f`**, então o que for trocado
  só no `.html` reaparece ou duplica no DOM final. Troca consistente: `.html`, o
  payload inline e os `.txt` (RSC). Sempre conferir o DOM pós-JS, não só o HTML.
- **Bundles em `_next/static/chunks/` têm cache de 1 ano no Cloudflare.** Bundle
  alterado ganha nome novo (sufixo `-m1`) e as referências em HTML/`.txt` são
  trocadas; o original fica intacto como rollback. O bundle novo sobe **antes**
  das páginas.
- **O HTML servido nunca bate byte a byte com o local**, porque o Cloudflare
  injeta o beacon do Insights, o bloco das JavaScript Detections (token muda a
  cada request) e a ofuscação de e-mail. Para comparar local × produção use
  `teste2mediex/ferramentas/cmp_prod.py`, que neutraliza as três.

## Ferramentas

```bash
python teste2mediex/serve.py                        # produção imitada em :8081
python teste2mediex/ferramentas/cmp_prod.py         # site/ × o que está no ar
python teste2mediex/ferramentas/rsc_verify_all.py   # integridade dos blocos T
```

## Não versionado

Dois arquivos ficam fora do git por guardarem credenciais em texto puro:

- `_ftp/config.json` — senha do FTP. Modelo em `_ftp/config.example.json`.
- `site/enviar-orcamento.php` — usuário e senha do SMTP da Locaweb. O código,
  sem as credenciais, está em `exemplos/enviar-orcamento.php`. **Não edite o
  arquivo real para remover a senha:** o `upload.py` compara hash e subiria a
  versão sem senha, derrubando a entrega de leads.

Também fora: `teste2mediex/site/` (cópia local, quase idêntica a `site/`) e
`.maestri/` (runtime local).
