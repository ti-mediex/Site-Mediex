# gtag.js carregado uma vez só (07/10/2026)

O layout tinha dois `<script async src="https://www.googletagmanager.com/gtag/js?id=...">`,
um do Ads (AW-18306236317) e um do GA4 (G-FVEDV9ECZD). O gtag carregado primeiro já
busca o container de cada ID configurado, então o GA4 era baixado duas vezes
(Lighthouse Treemap: 3 downloads, ~500 KiB). O loader do GA4 saiu: no payload
o elemento virou `null` e no HTML a tag foi removida. Os `gtag('config')` e o
listener de conversão continuam iguais.

Teste local com CDP (endpoints de coleta bloqueados): de 3 para 2 downloads,
com page_view do GA4, remarketing do Ads, conversão do WhatsApp
(WMn1CJabxfEcEJ3_i5lE) e clique_cta disparando igual ao antes.

`antes/` guarda os 465 arquivos de `site/` como estavam logo antes desta mudança,
já com a correção de schema da mesma data e ainda não publicados. Os originais
de produção ficam em `../2026-10-07-schema-seo/site-original/`.
