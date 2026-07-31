# Conferência do conjunto de regressão

Este documento mostra, na mão, como se chega a cada número de
`tests/fixtures/regressao/esperado.csv`. Ele existe para que o arquivo esperado
seja auditável: um golden file que ninguém sabe conferir não prova nada, só
congela o que o código fazia no dia em que foi gerado.

Cinco deputados fictícios, dez proposições, nove despesas. Pesos vindos do mapa
real do projeto (`legisdata/static/mapa_pesos_proposicoes.csv`):
PL = 1,0 · PEC = 1,0 · RIC = 0,6 · REQ = 0,4 · EMC = 0,3.

## Produtividade legislativa

Soma dos pesos das proposições que o deputado assina. Coautoria dá peso integral
a cada autor — a PEC 5 é assinada por 100 e por 400, e ambos recebem 1,0.

| Deputado | Proposições | Conta | Total |
|---|---|---|---|
| 100 | PL 1, REQ 3, REQ 4, PEC 5 | 1,0 + 0,4 + 0,4 + 1,0 | **2,8** |
| 200 | PL 2, RIC 6 | 1,0 + 0,6 | **1,6** |
| 300 | EMC 7, REQ 8 | 0,3 + 0,4 | **0,7** |
| 400 | PL 9, REQ 10, PEC 5 | 1,0 + 0,4 + 1,0 | **2,4** |
| 500 | REQ 10 | 0,4 | **0,4** |

## Gasto CEAP ajustado

Soma das despesas, excluindo as que têm `PASSAGE` na descrição ou `BSB` no
trecho.

| Deputado | Despesas | Excluída | Total |
|---|---|---|---|
| 100 | 12.000 + 3.000 | passagem BSB/CGH | **12.000** |
| 200 | 45.000 + 5.000 | — | **50.000** |
| 300 | 8.000 | — | **8.000** |
| 400 | 22.000 + 7.000 | PASSAGENS AÉREAS | **22.000** |
| 500 | 1.500 + 900 | táxi com trecho BSB/GIG | **1.500** |

Note o deputado 500: a despesa excluída é um táxi, não uma passagem aérea. O
filtro casa `BSB` em qualquer trecho, então pega deslocamento terrestre também.
É uma imprecisão conhecida da régua atual, fixada aqui de propósito.

## Quadrantes

Medianas da coorte: produtividade **1,6** e gasto **12.000**. O corte é `>=`,
então quem está exatamente na mediana cai no lado alto — caso dos deputados 200
(produtividade) e 100 (gasto).

| Deputado | Produtividade | Gasto | Quadrante |
|---|---|---|---|
| 100 | 2,8 ≥ 1,6 | 12.000 ≥ 12.000 | Alta produtividade e alto custo |
| 200 | 1,6 ≥ 1,6 | 50.000 ≥ 12.000 | Alta produtividade e alto custo |
| 300 | 0,7 < 1,6 | 8.000 < 12.000 | Baixa produtividade e baixo custo |
| 400 | 2,4 ≥ 1,6 | 22.000 ≥ 12.000 | Alta produtividade e alto custo |
| 500 | 0,4 < 1,6 | 1.500 < 12.000 | Baixa produtividade e baixo custo |

## Ranking composto

Duas posições independentes — produtividade decrescente e gasto crescente —
somadas, e a soma reordenada. Todas as três operações usam `method="dense"`.

| Deputado | Posição por produtividade | Posição por gasto | Soma | Ranking |
|---|---|---|---|---|
| 100 | 1 (2,8) | 3 (12.000) | 4 | **1** |
| 400 | 2 (2,4) | 4 (22.000) | 6 | **2** |
| 300 | 4 (0,7) | 2 (8.000) | 6 | **2** |
| 500 | 5 (0,4) | 1 (1.500) | 6 | **2** |
| 200 | 3 (1,6) | 5 (50.000) | 8 | **3** |

O empate triplo no 2º lugar não é acidente da amostra: a soma de posições produz
empates com facilidade e não há critério de desempate. Na base real de 512
deputados, isso comprime o ranking em 361 posições distintas.

## Eficácia de tramitação

Categorias por palavra-chave na situação: `norma jurídica`, `sanção`,
`promulgação` ou `senado` → sucesso; `arquivada`, `retirado`, `prejudic`,
`devolvida` ou `recusado` → fracasso; qualquer outra coisa → andamento.

| Deputado | Proposições | Sucesso | Fracasso | Andamento |
|---|---|---|---|---|
| 100 | 1, 3, 4, 5 | 2/4 = 0,50 | 1/4 = 0,25 | 1/4 = 0,25 |
| 200 | 2, 6 | 0 | 1/2 = 0,50 | 1/2 = 0,50 |
| 300 | 7, 8 | 0 | 1/2 = 0,50 | 1/2 = 0,50 |
| 400 | 9, 10, 5 | 2/3 = 0,667 | 0 | 1/3 = 0,333 |
| 500 | 10 | 0 | 0 | 1/1 = 1,00 |

A proposição 5 ("Remetido ao Senado Federal") conta como **sucesso** para 100 e
para 400, embora não tenha virado norma. É a régua vigente, e está no conjunto de
regressão justamente para que a revisão dela seja explícita.

## Temas de destaque

Os três temas mais frequentes do deputado, em texto corrido.

| Deputado | Contagem | Texto |
|---|---|---|
| 100 | Saúde ×3, Educação ×1 | Saúde e Educação |
| 200 | Economia ×2 | Economia |
| 300 | Cultura ×2 | Cultura |
| 400 | Segurança ×2, Saúde ×1 | Segurança e Saúde |
| 500 | Segurança ×1 | Segurança |
