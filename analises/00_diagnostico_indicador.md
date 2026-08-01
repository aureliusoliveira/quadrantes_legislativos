# Diagnóstico quantitativo do indicador de produtividade legislativa

**Data:** 31 de julho de 2026
**Base:** 57ª legislatura (2023–2026), dados da Câmara dos Deputados coletados em 31/07/2026
**Objetivo:** medir, antes de refatorar, se as críticas ao indicador atual se sustentam nos dados

---

## Sumário

O indicador atual é:

```
Pontuação = Σ (Peso_tipo × Ocorrência)
```

O diagnóstico testou oito problemas alegados. **Cinco se confirmam, um se confirma
por mecanismo diferente do suposto, um não se confirma e um não é testável sobre a
base atual.**

O achado central é este:

> **A correlação de Spearman entre o score atual e a contagem bruta de proposições
> é 0,995.**

O sistema de pesos — a única coisa que distingue este indicador de uma contagem —
não altera praticamente nada na ordenação. Ele produz o mesmo ranking que se
obteria contando proposições e ignorando o tipo. Todo o aparato metodológico de
pesos por relevância institucional é, empiricamente, decorativo.

---

## Nota de método

**Universo.** Das 271.826 proposições no bruto da legislatura, 165.145 têm peso
maior que zero no mapa vigente e entram no cálculo, gerando 323.594 linhas de
autoria distribuídas entre 706 parlamentares (o número excede 513 porque inclui
suplentes que exerceram em algum momento).

**Detecção de estágio.** A progressão foi reconstruída do arquivo consolidado de
tramitações (487.756 registros). O vocabulário da fonte é confiável para desfechos
terminais — "Transformação em Norma Jurídica", remessa ao Senado, arquivamento —
mas **subnotifica a aprovação em comissão**: o evento "Aprovação do Parecer"
aparece em apenas 0,5% das proposições legislativas, o que é implausível. Onde a
passagem por comissão importa, este relatório usa dois substitutos explícitos:
designação de relator e chegada a "Pronta para Pauta". Os percentuais de
progressão devem ser lidos como **limites**, não como medidas exatas.

**Reprodutibilidade.** Todos os números saem dos arquivos em `data/raw/` pelo
script de diagnóstico. Nenhum passo manual.

---

## P1 — Mede protocolo, não progressão · **CONFIRMADO**

Coorte: as **22.696 proposições legislativas** (PL, PLP, PEC, PDL, PLV, MPV, PRC)
**apresentadas por deputado** a partir de 1º/02/2023.

| Marco | Proposições | % |
|---|---:|---:|
| Apresentadas | 22.696 | 100,00% |
| Receberam relator designado | 6.448 | 28,41% |
| Chegaram a "Pronta para Pauta" | 1.487 | 6,55% |
| Passaram pelo Plenário | 452 | 1,99% |
| Transformadas em norma jurídica | 177 | **0,78%** |

**71,6% nunca tiveram sequer um relator designado, e menos de uma em cada cem
virou lei.** Apresentar tem custo marginal próximo de zero e o indicador remunera
integralmente esse ato. Um parlamentar que protocola 300 proposições que morrem no
protocolo supera, no ranking, um que aprovou duas leis.

**Contraste que dimensiona o problema.** As mesmas 4 categorias, considerando
*todos* os autores — Executivo, Senado, comissões e Mesa —, somam 25.669
proposições, das quais 687 viraram norma jurídica. Subtraindo a coorte de
deputados: as ~2.973 proposições de origem não parlamentar converteram cerca de
510 vezes, uma taxa da ordem de **17%**. Proposição de deputado converte a 0,78%.
A diferença é de aproximadamente **20 vezes**, e boa parte dela é composição — a
medida provisória é do Executivo por definição e converte alto. Ainda assim, é a
tese de Figueiredo & Limongi sobre o domínio da agenda pelo Executivo aparecendo
em um número. (Cálculo por diferença; merece verificação direta antes de virar
publicação.)

> **Ressalva de exposição.** Os percentuais acima são um retrato de 31/07/2026 e
> misturam proposições com 42 meses de tramitação e outras com dois. Servem para
> descrever esta legislatura; **não servem para comparar legislaturas** sem
> equalizar a janela de observação — ver a seção sobre censura à direita.

---

## P2 — Não distingue substância · **CONFIRMADO, POR OUTRO MECANISMO**

A hipótese do briefing era que proposições comemorativas e denominativas inflam o
score. **Isso não se confirma.** Por regex conservador sobre a ementa — "denomina",
"institui o Dia", "declara patrono", "confere o título" e variantes —, elas são
**687 de 22.708 proposições legislativas: 3,0%**. Removê-las desloca o parlamentar
mediano em 3 posições, com Spearman de 0,999 contra o ranking atual. É ruído
irrelevante.

O problema de substância existe, mas está em outro lugar: **na composição do
score**.

| Tipo | Ocorrências | % do score |
|---|---:|---:|
| REQ — Requerimento | 163.725 | **38,4%** |
| PRL — Parecer do Relator | 39.525 | **18,5%** |
| PL — Projeto de Lei | 26.427 | 15,5% |
| RIC — Requerimento de Informação | 20.393 | 7,2% |
| PEC — Proposta de Emenda à Constituição | 10.591 | 6,2% |
| EMC — Emenda na Comissão | 15.627 | 2,7% |
| EMP — Emenda de Plenário | 13.036 | 2,3% |
| INC — Indicação | 9.688 | 2,3% |

**Projeto de lei, PEC e afins somam 24,1% do score. Os outros 75,9% são
requerimento, parecer, emenda e indicação.** O indicador se chama "produtividade
legislativa" e três quartos dele não são produção legislativa.

---

## P3 — Ignora o desenho institucional brasileiro · **EVIDÊNCIA PARCIAL**

Não é testável como hipótese causal sobre esta base, mas a magnitude sustenta a
premissa: **39.525 pareceres de relator** na legislatura fazem da relatoria a
segunda maior massa de atividade parlamentar registrada, atrás apenas de
requerimentos.

Vale registrar o que se descobriu ao verificar isso. O mapa de pesos herdado
classificava a sigla `PRL` como "Projeto de Resolução Legislativa", com peso 0,8 —
próximo ao de um projeto de lei. A descrição oficial da fonte, em todas as 39.525
ocorrências, é **"Parecer do Relator"**. A sigla foi adivinhada errado, e o erro
respondia sozinho por 18,5% do score.

---

## P4 — Pesos arbitrários, sem análise de sensibilidade · **CONFIRMADO**

Este é o achado central, e ele é mais forte do que o briefing supunha.

| Comparação | Spearman |
|---|---:|
| Score atual × contagem bruta de proposições | **0,995** |
| Score atual × nº de proposições que avançaram de estágio | 0,792 |
| Contagem bruta × nº que avançaram de estágio | 0,787 |

Um sistema de pesos existe para diferenciar. Com ρ = 0,995 contra a contagem
simples, **os pesos não diferenciam nada**. O trabalho de atribuir relevância
institucional a cada tipo, que é a justificativa metodológica do indicador, não
produz efeito observável no resultado.

A consequência é a que o próprio TCC apontava em DIAP e Congresso em Foco: um
ranking cuja metodologia não é auditável porque, na prática, não é a metodologia
que determina o resultado.

---

## P5 — Coautoria não tratada · **CONFIRMADO**

**52,3% das linhas de autoria não são primeira assinatura.**

A concentração é o dado relevante: proposições com mais de 50 signatários são
**852 — 0,55% do universo — e geram 37,0% de todas as linhas de autoria e 32,4% do
score total**. A maior tem 333 assinaturas. A mediana de assinaturas por
proposição é 1.

Ou seja: um terço do que o indicador mede vem de meio por cento das proposições,
por adesão em massa.

O efeito no ranking depende de onde se olha:

| Critério alternativo | Spearman vs. atual | Deslocamento mediano | p95 |
|---|---:|---:|---:|
| Só primeira assinatura | 0,932 | 36 posições | **157** |
| Fracionado por nº de coautores | 0,943 | 36 posições | **143** |

A correlação alta engana. Ela é alta porque o topo não se move — quem lidera
lidera por volume próprio. No miolo da distribuição, o parlamentar do percentil 95
se desloca 157 posições numa base de 508. É a diferença entre o terço superior e o
terço inferior.

**O ranking é estável exatamente onde não é preciso e instável onde é.**

---

## P6 — Sem normalização por tempo de exercício · **CONFIRMADO, NÃO QUANTIFICADO**

Confirmado por caso e por contagem, mas ainda não medido: o cálculo de meses em
exercício exige o histórico de status por parlamentar, que não é coletado hoje.

O que se sabe:

- **98 dos 637 parlamentares com despesa têm menos de 12 meses de gasto na
  legislatura** (registrado em `docs/qualidade_dados.md`).
- O campo `situacao` da API **não identifica afastamento para cargo no Executivo**.
  Sônia Guajajara, Ministra dos Povos Indígenas, aparece na base como
  `situacao = "Exercício"`, com produtividade 7,5 e posição 160 no ranking —
  classificada como parlamentar de baixo desempenho. Marina Silva idem. Apenas 16
  dos 647 aparecem como "Licença".

O indicador atribui baixo desempenho a quem teve menor exposição, não menor
atuação. Como o dashboard nomeia pessoas, isso não é imprecisão estatística: é
afirmação errada sobre indivíduos identificados.

---

## P7 — Corte por mediana em distribuição assimétrica · **CONFIRMADO**

Distribuição do score na base atual:

| | |
|---|---:|
| Média | 241,5 |
| Mediana | 170,6 |
| Desvio padrão | 492,6 |
| Máximo | 8.642,3 |
| Razão 1º / mediana | **51x** |
| Concentração no top 5% | 31,8% do score total |

Desvio padrão duas vezes maior que a média confirma a assimetria. E a
classificação é instável na borda:

| Deslocamento da mediana | Parlamentares que mudam de quadrante |
|---|---:|
| +5% | 59 de 508 (**11,6%**) |
| −5% | 53 de 508 (**10,4%**) |

Uma variação de 5% num parâmetro que ninguém escolheu — a mediana é o que a base
der — reclassifica um em cada dez parlamentares. O quadrante, que é a mensagem
principal do produto, não é robusto.

---

## P8 — "Custo do mandato" é só CEAP · **PROCEDE (factual)**

Não é hipótese a testar, é descrição correta. A dimensão cobre exclusivamente a
cota parlamentar. Ficam de fora subsídio, verba de gabinete, pessoal, auxílio-moradia
e estrutura. O nome promete o custo do mandato e entrega uma fração declarada dele.

---

## Nota metodológica: censura à direita

Vale registrar porque condiciona qualquer uso comparativo destes números, e porque
foi um erro cometido na primeira versão deste relatório.

Uma proposição apresentada em junho de 2026 teve dois meses para tramitar. Uma de
fevereiro de 2023 teve quarenta e dois. Ao contar quantas viraram lei num retrato
de hoje, as duas entram na mesma conta — e a que ainda não teve tempo é registrada
como fracasso, quando o correto seria "ainda não se sabe". O desfecho existe, mas
está **à direita** do momento em que se olhou.

O efeito não é pequeno. Na coorte da 57ª legislatura:

| Exposição desde a apresentação | Proposições | % da coorte |
|---|---:|---:|
| ao menos 6 meses | 17.786 | 78,4% |
| ao menos 12 meses | 14.224 | 62,7% |
| ao menos 24 meses | 8.709 | 38,4% |
| ao menos 36 meses | 3.502 | 15,4% |

**Só 38% da coorte teve dois anos de exposição.** E a taxa de conversão muda
conforme se corrige isso:

| Critério | Taxa de conversão em lei |
|---|---:|
| Retrato de hoje, todas as proposições | 0,78% |
| Janela fixa de 12 meses (n = 14.224) | 1,19% |
| Janela fixa de 24 meses (n = 8.709) | 1,50% |

A medida ingênua **subestima a conversão pela metade** em relação à coorte com
janela de 24 meses. E, pior para comparação: o viés depende de quando se tirou o
retrato e de como as apresentações se distribuem no tempo — duas coisas que variam
entre legislaturas.

**Consequência prática.** Comparar o funil de uma legislatura em curso com o de uma
encerrada mede truncamento, não desempenho: a em curso sempre parecerá pior. A
correção é medir cada proposição num relógio próprio — o estágio atingido **até N
meses após a sua apresentação**, com o mesmo N para todas — o que exige descartar
da comparação tudo que foi apresentado há menos de N meses. Perde-se base e
ganha-se comparabilidade.

Os dados permitem: cada tramitação traz `dataHora`, então o estágio dentro de
qualquer janela é reconstruível.

---

## Achado adicional: a escala é toda relativa à própria coorte

Não constava do briefing. Mediana, quadrante e ranking são definidos pela
distribuição da legislatura corrente. Não há âncora absoluta.

Isso torna **impossível** responder à pergunta que o PRD elege como diferencial do
produto — "esse deputado melhorou ou piorou em relação à legislatura anterior?" —
porque o critério de comparação se move junto com o comparado. Um parlamentar pode
piorar em termos absolutos e subir de quadrante se a coorte piorar mais.

---

## Conclusão

O indicador atual não mede produtividade legislativa. Ele conta atos parlamentares,
com um sistema de pesos que — comprovadamente, ρ = 0,995 — não altera o resultado
dessa contagem. Três quartos do que ele soma não são produção legislativa, e 99,2%
das proposições legislativas que ele premia não viraram lei.

Nenhum desses problemas é de implementação. O pipeline que produz o número é
reproduzível, testado e reconciliado com a fonte — o número errado é calculado
corretamente. São problemas de construto: o indicador mede uma coisa e afirma medir
outra.

**Implicações para a refatoração:**

1. Medir progressão, e não protocolo, é a mudança de maior efeito — separa 2,7% de
   100%, enquanto o ajuste de comemorativas separa 3% de ruído irrelevante.
2. A coautoria precisa de regra explícita; a escolha entre "primeira assinatura" e
   fracionamento move 157 posições no percentil 95 e não pode ficar implícita.
3. A normalização por tempo de exercício exige coletar o histórico de status, que
   hoje não é coletado. É pré-requisito, não refinamento.
4. Qualquer sistema de pesos novo precisa passar por análise de sensibilidade antes
   de entrar. O sistema atual não passaria pelo teste mais básico: ele não muda o
   ranking em relação a não ter peso nenhum.
5. A escala relativa é decisão de arquitetura do indicador e precisa ser resolvida
   antes, não depois, se a comparação entre legislaturas for para permanecer no
   escopo do produto.

**Ressalva de método:** a subnotificação da aprovação em comissão na fonte impede
medir com precisão o estágio intermediário. Os percentuais de P1 são limites
superiores de mortalidade, e a construção de um multiplicador de estágio confiável
exige antes resolver essa lacuna de vocabulário — provavelmente cruzando
`codSituacao`, órgão e despacho, com validação manual por amostra.
