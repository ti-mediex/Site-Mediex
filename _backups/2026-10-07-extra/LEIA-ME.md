# Pendências menores (07/10/2026)

`antes/` guarda os arquivos de `site/` como estavam logo antes desta etapa (já com a
correção de schema e o gtag único, nenhum dos dois publicado ainda).
`lista-arquivos.json` lista os 338 caminhos. O bundle novo não tem versão "antes".

1. **Empresa em dobro no schema**: o JSON-LD `MedicalBusiness` de página (50 páginas
   de cidade e /exame-admissional-recife) declarava uma segunda empresa (nome
   diferente, sem @id, mesmo endereço) além da MedicalClinic #clinic do layout. O
   elemento `<script>` virou `null` no payload e saiu do HTML. O `Service` com
   `provider` das páginas de cidade continua.
2. **Nota antiga visível → 4,6**:
   - CTA dos 32 posts do blog: o texto vive no bundle `0webri5l62s6_.js`, que tem
     cache de 1 ano no Cloudflare. Foi criado `0webri5l62s6_-m1.js`, idêntico
     exceto "5.0 no Google" → "4,6 no Google" (e idêntico ao que a sessão de
     24/09 preparou no teste2mediex). Todas as referências (tag `<script>`,
     elemento do payload e lista de chunks) passaram para o nome novo. O original
     fica no servidor como rollback.
   - links.html / links.txt / links/__next.links/__PAGE__.txt: "5,0 no Google".
   - llms.txt: "Avaliacao no Google: 4,6 (407 avaliacoes)".

**Ordem de upload**: suba o `_next/static/chunks/0webri5l62s6_-m1.js` ANTES das
páginas. Um 404 de asset pedido durante o deploy fica 4h em cache no Cloudflare.

**Reverter**: copiar `antes/` por cima de `site/` e subir.
