---
name: anuncios-google-ads
description: Escrever, revisar e iterar anúncios responsivos de pesquisa (RSA) do Google Ads para a Mediex — títulos, descrições, caminhos de exibição, nomenclatura de campanha e diagnóstico de desempenho, respeitando limites de caractere e as regras de política do setor de saúde e segurança do trabalho. Use ao criar anúncios de um grupo, revisar textos existentes, gerar variações para teste, montar o CSV de importação ou decidir o que pausar a partir dos números.
---

# Anúncios do Google Ads — RSA

Skill interna deste projeto. Arquivo único, sem dependência externa, sem script,
sem telemetria. Nada aqui manda enviar dado para lugar nenhum.

## Quando usar

- Criar os anúncios de um grupo novo
- Revisar títulos e descrições já escritos
- Gerar variações para teste
- Montar o CSV de importação em massa
- Diagnosticar um grupo que gasta e não converte

## Antes de escrever, tenha em mãos

Se algum item faltar, **pergunte antes de gerar** — anúncio escrito sem isso vira texto genérico.

1. **Termo do grupo** — a palavra-chave exata que dispara o anúncio (ex.: "pcmso recife")
2. **Estágio de consciência** de quem busca esse termo (ver matriz abaixo)
3. **Página de destino** — qual URL recebe o clique
4. **Oferta concreta** — o que a pessoa recebe se clicar
5. **Cidade** — a segmentação daquele grupo
6. **Objeção principal** — o que faz a pessoa não fechar
7. **Dados de desempenho**, se for iteração — o que está rodando e como vai

---

## A regra de ouro do RSA

**O Google combina os títulos aleatoriamente.** Cada título precisa fazer sentido
sozinho e ao lado de qualquer outro do conjunto.

Escrever títulos que só funcionam em sequência — "Documentação de SST" + "em um só
contrato" — é o erro nº 1 do formato: o anúncio pode ir ao ar como
"em um só contrato | Recife e Região", que não diz nada.

Teste rápido: pegue três títulos ao acaso, monte na ordem que caiu e leia em voz alta.
Se não fizer sentido, reescreva.

## Especificações técnicas

| Elemento | Quantidade | Limite |
|---|---|---|
| Títulos | até 15 | **30 caracteres** |
| Descrições | até 4 | **90 caracteres** |
| Caminho de exibição | 2 campos | **15 caracteres** cada |

- Títulos podem ser **fixados** nas posições 1, 2 ou 3; descrições, nas 1 ou 2.
- Fixar reduz combinações e derruba a "Força do anúncio" — fixe só o que for obrigatório.
- Contar caractere inclui **espaço e pontuação**. Acento conta 1.
- O conjunto precisa ter, no mínimo: **1 título com a palavra-chave**, **1 de benefício**
  e **2 a 3 de chamada para ação**.

---

## Estágio de consciência — escolha o gancho certo

Quem digitou cada termo está num momento diferente. Um único estilo de título para
todos os grupos desperdiça o clique.

| Estágio | Como reconhecer | O que o título deve liderar |
|---|---|---|
| Não sabe do problema | "obrigações do empregador" | reconhecimento do problema, identidade |
| Sabe do problema | "quem faz pcmso", "documento obrigatório" | a dor, o custo, a contradição |
| Conhece a solução | "empresa de pcmso", "clínica ocupacional" | diferenciação e mecanismo |
| Conhece o fornecedor | "pcmso recife preço" | prova e benefício preciso |
| Pronto para agir | "pcmso recife orçamento" | a próxima ação, direta |

## Nível de confiança — regra para a Mediex

Quem chega de anúncio **não conhece a marca**. Confiança baixa significa:

> **clareza vence mistério.**

Nada de curiosidade vaga ("O erro que 9 em 10 empresas cometem"). Diga o que é,
para quem é e onde fica. Curiosidade com prova só serve para quem já ouviu falar
da empresa; tensão e ousadia, só para quem já é cliente.

---

## Método de geração

### 1. Ângulos

Não escreva 15 títulos sobre a mesma ideia. Distribua entre ângulos — cada um fala
com uma pessoa diferente:

| Ângulo | O que explora |
|---|---|
| Termo exato | espelha a busca, palavra por palavra |
| Dor | prazo vencido, evento pendente, fiscalização |
| Solução | tudo em um contrato, um só responsável |
| Autoridade | médico coordenador, responsável técnico |
| Prova | anos de atuação, avaliações, clientes |
| Local | cidade, região, clínica própria |
| Ação | orçamento, WhatsApp, proposta |

### 2. Geração em ondas

Produzir 15 títulos de uma vez leva a 15 variações da mesma frase. Faça em três ondas:

- **Onda 1** — ângulos centrais: 3 a 5 ângulos, 3 variações cada
- **Onda 2** — extensões dos 2 ângulos mais fortes
- **Onda 3** — carta fora do baralho: contraintuitivo, específico demais, direto demais

Depois filtre: corte o que estourou o limite, corte quase-duplicatas, sinalize
qualquer coisa que roce a política e confira se as combinações fazem sentido.

### 3. Variação dentro do ângulo

- **Palavra** — sinônimos, verbo no lugar de substantivo
- **Especificidade** — número concreto no lugar de afirmação geral
- **Tom** — afirmação, pergunta, comando
- **Comprimento** — alguns com 18–22 caracteres, outros com 27–30

### 4. Descrições

Descrição **não repete título** — ela complementa. Use os 4 espaços para:

1. **Prova** — número verificável
2. **Objeção** — o que trava a decisão
3. **Chamada para ação** — o próximo passo, explícito
4. **Escopo** — o que está incluso

Primeira frase entrega o benefício, segunda chama para a ação.

---

## Padrões de qualidade

**Título bom:**
- Específico ("PCMSO com médico responsável") no lugar de vago ("Qualidade em SST")
- Benefício no lugar de característica
- Voz ativa
- Número quando houver ("15 anos", "407 avaliações")

**Título ruim:**
- Jargão que o cliente não usa
- "Melhor", "Líder", "Referência" sem nada que sustente
- CAPS LOCK, "!!", símbolo decorativo
- Promessa que a landing page não cumpre

**Continuidade da promessa:** o que o título promete, a página tem que entregar na
primeira dobra. Anúncio que promete preço e cai numa página sem preço queima verba
duas vezes — no clique e na confiança.

---

## Regras de política — obrigatórias

Não são preferência de estilo. São o que reprova anúncio ou gera notificação.

**Nunca prometer conformidade ou ausência de risco:**
- ❌ "100% em conformidade" · "garantia contra multa" · "sem risco de autuação" · "evite multas"
- ✅ "documentos com responsável técnico" · "eventos transmitidos com recibo" · "prazos acompanhados"

**Nunca citar concorrente no texto.** Marca de terceiro pode ser palavra-chave, mas não
pode aparecer no anúncio nem na página. É a causa mais comum de notificação extrajudicial
neste mercado.

**Nunca sugerir diagnóstico ou condição de saúde de pessoa.** A oferta é B2B e documental.
Falar da saúde de indivíduo entra em categoria sensível e restringe a conta.

**Nunca prometer prazo ou preço não fechado.** "Proposta no mesmo dia" só se o
atendimento garantir isso dentro do horário comercial.

**Sem falsa escassez.** "Últimas vagas" numa oferta de contrato recorrente é mentira
detectável e derruba a confiança.

---

## Checklist de validação

Reprovou, reescreve.

- [ ] Todo título com no máximo 30 caracteres, **contados, não estimados**
- [ ] Toda descrição com no máximo 90
- [ ] Caminhos com no máximo 15 cada
- [ ] Cada título faz sentido sozinho e em qualquer combinação
- [ ] Termo do grupo em pelo menos 3 títulos
- [ ] Pelo menos 2 títulos de chamada para ação
- [ ] Pelo menos 1 de prova e 1 de localização
- [ ] Nenhum par dizendo a mesma coisa com outras palavras
- [ ] Descrições complementam, não repetem os títulos
- [ ] Nenhuma promessa proibida
- [ ] Nenhum nome de concorrente
- [ ] A landing page entrega o que o anúncio promete

---

## Formato de saída

**1. Títulos com contagem visível e alternativa para o que estourou:**

```
TÍTULOS (máx. 30)
 1. [FIXO pos.1] PCMSO em Recife              (15)
 2.              Documentação de SST em dia    (28)
 3.              PCMSO com médico responsável  (28)
 4.              Programas de SST sem dor de cabeça  (34)  ESTOUROU
    →            SST sem dor de cabeça         (21)

DESCRIÇÕES (máx. 90)
 1. ...  (87)
```

**2. CSV para o Google Ads Editor:**

```csv
Campaign,Ad group,Headline 1,...,Headline 15,Description 1,...,Description 4,Final URL,Path 1,Path 2
```

**3. Observações** — o que foi fixado e por quê, e quais títulos são candidatos a
troca no primeiro relatório de recursos com desempenho "Baixo".

## Nomenclatura

Padrão consistente, para o relatório ficar legível depois:

```
GADS_[Tipo]_[Serviço]_[Cidade]
Ex.: GADS_Search_PCMSO_Recife · GADS_Search_eSocial_RMR
```

---

## Iteração a partir de dados

**Antes de julgar qualquer anúncio: espere 1.000+ impressões.** Abaixo disso o número
é ruído, não sinal.

Ao receber os dados:

1. **Vencedores** — que tema, que estrutura (pergunta? número? comando?), que
   comprimento aparece nos melhores?
2. **Perdedores** — que ângulo não ressoou? Genérico demais? Longo demais?
3. **Nova rodada** — reforce o tema vencedor com frases novas, estenda os ângulos que
   funcionaram, teste 1 ou 2 ângulos inéditos, elimine os padrões dos piores.
4. **Registre** — data, top e bottom, padrão observado, ângulos aposentados.

**Mude uma variável por ciclo.** Trocar título e página ao mesmo tempo não diz qual
das duas coisas mexeu no resultado.

### Diagnóstico por sintoma

**Custo por lead alto:**
1. Olhe a página primeiro — o problema é pós-clique?
2. Termos de pesquisa: está entrando busca irrelevante?
3. Ângulo do anúncio não bate com a intenção do termo
4. Índice de qualidade baixo → relevância entre termo, anúncio e página
5. Só então mexa no lance

**CTR baixo:** o texto não ressoa, ou o termo atrai gente errada, ou a oferta é fraca.

**Muita impressão e nenhum clique:** provavelmente o termo é amplo demais — negative
keyword antes de mexer no criativo.

### Cuidado com atribuição

A plataforma **infla o próprio crédito** — ela quer receber o mérito. Compare sempre
o número do Ads com o do GA4, e olhe o custo por cliente fechado, não só o custo
por lead da plataforma.

---

## Limite realista de teste A/B neste projeto

O cenário provável do plano é ~52 leads/mês. Significância estatística de verdade
pede volume que essa conta **não vai ter em poucas semanas**.

Consequência prática: trate os testes como **direcionais, não conclusivos**. Não
mate um título por causa de 40 cliques. Prefira mudanças grandes (ângulo inteiro) a
ajustes finos de palavra — só as grandes aparecem em volume baixo.

---

## Contexto fixo da Mediex

Dados verificados no site. Use estes, não invente outros:

- **Telefone/WhatsApp**: (81) 3072-9818 · `wa.me/558130729818`
- **Endereço**: R. Gen. Góes Monteiro, 448 — Imbiribeira, Recife/PE
- **Horário**: seg–qui 7h–17h · sex 7h–16h
- **Prova**: 15+ anos · 500+ clientes ativos · 50 mil+ vidas · 4,6 no Google com 407 avaliações
- **Landing page do PGD**: `https://mediex.com.br/pgd/` (com barra final, evita um 301)
- **Serviços**: PCMSO, PGR, LTCAT, insalubridade, periculosidade, eSocial SST (S-2220, S-2240)
- **Cobertura**: Recife e Região Metropolitana
- **Conversões já instaladas**: GA4 `G-FVEDV9ECZD` · Ads `AW-18306236317`

---

## Erros que aparecem sempre

- Títulos que só funcionam em sequência — o Google embaralha
- Estourar 30 caracteres por estimar em vez de contar
- 15 títulos que são a mesma frase reescrita
- Nenhum título de ação — o conjunto informa e não convida
- Descrição genérica do tipo "Saiba mais sobre nossos serviços": desperdiça o espaço
- Fixar 3 títulos e 2 descrições e sufocar as combinações
- Reusar o mesmo conjunto em todos os grupos trocando só a cidade
- Aposentar criativo cedo demais, antes de 1.000 impressões
- Prometer o que a landing page não entrega
