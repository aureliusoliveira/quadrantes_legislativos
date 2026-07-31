# Qualidade de dados — investigação do gasto CEAP

Registro da investigação do "M1": deputados aparecendo no topo do ranking
publicado com gasto CEAP implausível (Amom Mandel com R$ 15,19 e Ricardo Barros
com R$ 832,77, contra mediana de R$ 872 mil).

## Hipóteses descartadas

Duas hipóteses iniciais estavam erradas, e vale registrar por quê:

**Chave que não casa.** `ideCadastro` do CEAP corresponde ao `id` do deputado na
API. Amom Mandel tem 178 linhas sob `ideCadastro = 220715`, todas atribuídas
corretamente. Não há problema de junção.

**Separador decimal.** `vlrLiquido` chega como float já parseado, e
`pd.to_numeric` não introduz nenhum nulo em 672 mil linhas. Não há perda por
conversão.

## Causa real: o artefato publicado é uma cópia velha da fonte

Recalculando o gasto ajustado a partir do CEAP baixado hoje, com a mesma regra de
produção, e comparando com o `resultados.csv` publicado:

| | |
|---|---|
| deputados com valor publicado **menor** que a fonte | **510 de 510** |
| deputados com valor publicado maior | 0 |
| soma publicada | R$ 401.523.562 |
| soma recalculada | R$ 578.912.938 |
| **subestimação** | **R$ 177.389.375 (30,6%)** |
| razão fonte/publicado, mediana | 1,42x |
| razão fonte/publicado, máxima | 307x |

Nenhuma exceção em 510 casos elimina coincidência. O caso extremo é Zé Adriano
(AC): R$ 27.081 publicados contra R$ 557.276 na fonte.

A causa é o checkpoint da coleta (`ColetorBase._ja_baixado`), que marca o par
`(tipo, ano)` como baixado em definitivo. O CEAP é **restatement**: a Câmara
republica o arquivo do ano conforme as despesas são processadas. Baixado uma vez,
o ano fica congelado no estado em que estava, e tudo que a fonte publicou depois
nunca chega ao pipeline.

Isso reclassifica o problema: não é bug de cálculo, é o pipeline não ter noção de
reprocessamento. O mesmo defeito congela as métricas de eficácia de tramitação.

## O caso Amom Mandel não é erro

Investigado à parte, porque a conclusão é diferente. Seu gasto na legislatura:

| Categoria | Linhas | Valor |
|---|---|---|
| PASSAGEM AÉREA - SIGEPA | 159 | R$ 65.318,81 |
| TELEFONIA | 19 | R$ 22,04 |

Ele de fato só usa a cota para passagem aérea. O gasto bruto de R$ 65 mil na
legislatura inteira é uma ordem de grandeza abaixo dos colegas (mediana bruta na
casa de R$ 1 milhão). O ajuste que remove passagens leva o valor a R$ 22, mas ele
lideraria o ranking de qualquer forma. **O número está certo e a posição é
legítima** — o que a apuração jornalística faria com isso é outra conversa.

## Achados secundários

**Estornos como valor negativo.** Oito parlamentares têm soma bruta negativa na
legislatura 57 — são restituições de despesas da legislatura anterior, pagas
durante a atual e etiquetadas com `codLegislatura = 57`. O recorte por
legislatura captura a devolução sem a despesa que a originou.

**Mandatos parciais comparados com mandatos inteiros.** Dos 637 parlamentares com
despesa na legislatura, 98 têm menos de 12 meses de gasto — suplentes,
substituições e quem saiu para assumir cargo no Executivo. O gasto absoluto de
quem serviu 8 meses é comparado com o de quem serviu 35, sem normalização.

**`on_bad_lines="skip"` nos carregadores.** Não descartava nenhuma linha nos
arquivos atuais, mas descartaria em silêncio se a fonte publicasse arquivo
malformado. Substituído por leitura estrita que interrompe a carga apontando o
arquivo.

## O que ficou coberto por teste

- `tests/test_qualidade_dados.py` — invariantes do artefato publicado
  (unicidade, nulos, faixas, quadrantes, ranking, UFs, percentuais). Roda no CI.
- `tests/test_reconciliacao_gastos.py` — compara o número publicado com a fonte
  bruta, usando a regra de produção. Pulado quando não há `data/raw/`.

O teste de reconciliação está marcado `xfail(strict=True)` enquanto o artefato
publicado for o antigo. Quando o Incremento 5 regenerar os dados, ele passa a
falhar por estar passando — e o marcador sai.

**Nenhuma invariante interna detectou o problema**: as 14 do artefato publicado
passam. Um resultado calculado sobre fonte obsoleta é perfeitamente consistente
consigo mesmo. Só a comparação com a fonte revela — é o que sustenta a métrica
"zero divergência entre número exibido e dado bruto" do PRD.
