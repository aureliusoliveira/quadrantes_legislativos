# Universo de proposições e pesos

Decisão metodológica de 31 de julho de 2026, tomada quando a troca da fonte
expôs uma escolha que até então estava implícita no código.

## O que aconteceu

Até esta carga, as proposições vinham da API paginada da Câmara. Passaram a vir
do arquivo consolidado anual, que é a mesma fonte oficial — só que completa. O
efeito não foi de volume: foi de **universo**.

O arquivo consolidado trouxe 75 tipos de proposição que o pipeline nunca tinha
visto. Deles, 61 aparecem com deputado como autor, somando **134 mil registros —
31,7% de tudo que tem autoria de deputado na 57ª legislatura**.

Não era dado novo escondido. Era dado que a coleta antiga não alcançava, e cuja
ausência ninguém tinha decidido: simplesmente não chegava.

A guarda no `IndicadoresProposicoes` interrompeu a carga em vez de tratar tipo
desconhecido como peso zero. Foi ela que transformou uma omissão silenciosa numa
decisão explícita — que é exatamente o que ela existe para fazer.

## O que esses tipos são

Misturam duas coisas de natureza diferente:

| | Exemplos | Volume |
|---|---|---|
| Ato de procedimento e documento de tramitação | `RPD` Requerimento de Votação pelo Processo Nominal, `DOC` Documento, `ATA` Ata, `OF` Ofício, `RDF` Redação Final, `DTQ` Destaque para Votação em Separado | `RPD` sozinho: 76.199 |
| Trabalho de relatoria e de colegiado | `PAR` Parecer de Comissão, `PPP` Parecer Proferido em Plenário, `VTS` Voto em Separado, `REL-A` Relatório Adotado pela Comissão | ~5 mil |
| Iniciativa de mérito legislativo | `EMP` Emenda de Plenário, `EMR` Emenda de Relator, `ESB` Emenda ao Substitutivo, `INC` Indicação, `RCP` Requerimento de CPI, `PFC` Proposta de Fiscalização e Controle | ~30 mil |

Tratar os três grupos igual seria absurdo em qualquer direção. Contar tudo faria
o deputado que mais pede votação nominal liderar a produtividade legislativa.
Ignorar tudo descartaria 30 mil emendas e indicações — produção real.

## Critério adotado

**Peso maior que zero para a peça que propõe criação ou alteração de matéria.
Peso zero para a peça de instrução, o documento e o registro.**

Emenda conta, inclusive a de relator: ela muda o texto que vai a voto. Parecer,
relatório e voto em separado não contam: são a instrução do processo, produzidos
por designação e não por iniciativa. Ata, ofício, documento e redação final são
registro. Requerimento de votação nominal e destaque são condução de sessão.

Os pesos novos usam a escala que já existia, por analogia:

| Faixa | Tipos |
|---|---|
| 0,6 | `RCP` (CPI), `PFC` (fiscalização e controle), `SIT` (informação ao TCU) — instrumentos de controle, na faixa do `RIC` |
| 0,4 | `INC` Indicação, na faixa do `IND` que já constava |
| 0,3 | Família da emenda: `EMP`, `EMR`, `ESB`, `EMA`, `EML`, `EMO`, `SBE`, `SBR`, `SSP`, e as sugestões de emenda orçamentária `SLD`, `SOR`, `SPP` — mesma faixa do `EMC` |
| 0,2 | Iniciativas de volume marginal: `CON`, `PRO`, `SUG`, `REM`, `REP`, `PIN`, `APJ`, `INA` |
| 0,1 | `ERD` Emenda de Redação — altera texto sem alterar mérito |
| 0,9 | `SAP` Sustação de Andamento de Ação Penal |
| 0 | Os 49 restantes |

A tabela vive em `legisdata/static/mapa_pesos_proposicoes.csv`, versionada com o
código. Mudar um peso é mudar o produto, e o histórico do arquivo é o registro de
quando e por quê.

### Julgamentos discutíveis, registrados como tais

- **Emenda de relator e subemenda de relator contam.** São produzidas no
  exercício da relatoria, o que puxaria para peso zero pelo critério de
  "iniciativa". Contam porque alteram o texto da matéria — o efeito legislativo
  é o mesmo de qualquer emenda. Quem discordar tem argumento.
- **Peças "adotadas pela comissão" (`EMC-A`, `SBT-A`, `REL-A`) valem zero.** A
  adoção pelo colegiado registra de novo uma peça que já existe; contá-las seria
  contar duas vezes o mesmo trabalho.
- **Sugestões de emenda orçamentária de comissão (`SLD`, `SOR`, `SPP`) contam
  0,3.** A autoria formal é do colegiado, mas o registro traz o deputado
  proponente, e a peça altera matéria orçamentária.
- **`SAP` vale 0,9** por ser instrumento constitucional de peso, apesar de não
  ter ocorrência na legislatura.

## O universo vale para as duas dimensões

Peso zero não diz "vale pouco". Diz **"isto não é produção legislativa do
parlamentar"**. Uma vez dito, vale para tudo que o produto publica:

- **Produtividade legislativa** — soma dos pesos; tipo de peso zero não soma.
- **Taxas de eficácia** (`pct_sucesso`, `pct_fracasso`, `pct_andamento`) —
  calculadas apenas sobre as proposições que contam como produção. Sem isso, os
  76 mil requerimentos de votação nominal entrariam no denominador e as taxas
  passariam a descrever o destino do procedimento de plenário, não o da produção
  do parlamentar.
- **Temas de destaque** — pela mesma razão, extraídos do mesmo universo. O tema
  mais frequente de um deputado deve sair do que ele propôs, não dos documentos
  que sua atividade gerou.

A regra está em `MapaDePesos.producao`, aplicada num único ponto
(`IndicadoresGerais`), e coberta por
`tests/indicadores/test_gerais.py::test_tipo_de_peso_zero_nao_entra_em_nenhuma_dimensao`.

## Efeito sobre os números publicados

Os números mudam, e mudam por dois motivos somados: o universo passou a ser o
completo, e o CEAP deixou de ser uma cópia congelada de 2024 (ver
`qualidade_dados.md`). Comparação direta com o `resultados.csv` anterior não é
comparação de mesma metodologia.

Isso é uma quebra consciente da série. A alternativa — manter o universo antigo
para preservar continuidade — foi considerada e descartada: preservaria a
comparabilidade com um retrato que já estava errado.

## O que fica em aberto

- **Emenda vale um terço de um projeto de lei?** A escala de pesos foi herdada
  do TCC e nunca foi validada contra literatura de ciência política. O critério
  de universo, decidido aqui, é independente dessa calibragem — mas a calibragem
  continua devendo justificativa.
- **Coautoria.** Uma proposição com dez assinaturas soma peso cheio para os dez.
  É decisão anterior a esta e segue valendo, sem ter sido examinada.
- **Mandato parcial.** Quem exerceu oito meses é comparado com quem exerceu 35,
  sem normalização, nas duas dimensões.
