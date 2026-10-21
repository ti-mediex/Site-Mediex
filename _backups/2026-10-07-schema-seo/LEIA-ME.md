# Correção de schema / hidratação (07/10/2026)

`site-original/` guarda os 468 arquivos de `site/` no estado em que estavam ANTES
desta correção, idêntico ao que estava em produção. `lista-arquivos.json` lista os
caminhos.

## O que mudou

1. **MedicalClinic (layout, todas as páginas)**: saíram `aggregateRating` e `review`.
   A nota é da própria clínica (o Google não mostra estrelas para isso em
   LocalBusiness) e vinha do Google Maps (as diretrizes pedem para não marcar
   avaliações de outro site). No payload RSC, o JSON-LD é um bloco T
   (`id:T<hex>,<json>`); o tamanho em bytes foi recalculado.
2. **FAQPage do layout**: as 6 perguntas ("Quais exames ocupacionais a Mediex
   realiza?" e outras) não aparecem visíveis em página nenhuma. A linha do payload
   com o elemento `<script>` virou `null` e o `<script type="application/ld+json">`
   saiu do HTML. O bloco T com o texto ficou no payload, sem referência e inerte.
   Os FAQPage próprios das páginas de serviço continuam.
3. **/exame-admissional-recife**: a MedicalBusiness perdeu `aggregateRating`
   (4.5/351), e "4,5" virou "4,6" no payload, porque o HTML já dizia 4,6 e essa
   diferença causava o erro #418 do React.
4. **pgd/index.html** (HTML puro): saiu `aggregateRating` do JSON-LD.
5. **.htaccess**: `Redirect 301 /medicina-do-trabalho(/) /`.

Causa raiz do schema duplicado em produção: o Google Tag Gateway do Cloudflare
injetava 3 `<script>` no início do `<head>` (só para navegadores). Isso causava
o #418, o React redesenhava a página com o payload antigo e o `<head>` saía em
dobro. O gateway foi desligado no painel em 07/10/2026; não reativar com
injeção automática.

## Como reverter

Copiar o conteúdo de `site-original/` por cima de `site/` e subir com
`python _ftp/upload.py --go`. Para reverter só o `.htaccess`, subir só ele.
