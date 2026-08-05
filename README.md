# Quadrantes da Produtividade Legislativa

[![CI](https://github.com/aureliusoliveira/quadrantes_legislativos/actions/workflows/ci.yml/badge.svg)](https://github.com/aureliusoliveira/quadrantes_legislativos/actions/workflows/ci.yml)
[![Dashboard](https://img.shields.io/badge/dashboard-online-005EB8)](https://quadranteslegislativos.streamlit.app/)

**▶ [Ver o dashboard](https://quadranteslegislativos.streamlit.app/)**

Pipeline de dados que cruza **custo de mandato** (CEAP) e **produtividade legislativa** de deputados federais brasileiros, a partir dos dados abertos da Câmara, e publica o resultado num dashboard interativo. Os parlamentares da 57ª legislatura são posicionados em quatro quadrantes, com metodologia aberta e auditável.

**Stack:** Python 3.12 · pandas · Plotly · Streamlit · pytest · uv · GitHub Actions.

**O ciclo completo:** coleta na API da Câmara e nos arquivos de despesa → padronização e reconciliação das bases → cálculo dos indicadores → publicação do artefato servido ao dashboard. Cada etapa tem teste, e nenhum teste depende de rede.

O escopo, os não-objetivos e as fases estão no [PRD](docs/quadrantes_prd_v1.md).

> **Estado atual: Fase 1 (Fundação), em andamento.** Há divergências conhecidas entre a metodologia documentada e a implementada, e valores de gasto CEAP sob investigação. Veja [Limitações conhecidas](#limitações-conhecidas) antes de citar qualquer número.

## Estrutura

```
├── legisdata/            # coleta e cálculo de indicadores
│   ├── coleta/           # coletores por fonte (API da Câmara, arquivos CEAP)
│   ├── processamento/    # carregamento e padronização das bases
│   ├── indicadores/      # regra de negócio: produtividade, gastos, tramitação, temas
│   └── config.py
├── dashboard/            # app Streamlit de página única
│   ├── app.py            # entrypoint do Streamlit Cloud e a própria visualização
│   ├── graficos.py       # gráfico de quadrantes (Plotly)
│   └── data/             # resultados.csv servido ao dashboard
├── tests/
├── docs/
├── notebooks/
├── main_coleta.py        # pipeline de coleta
└── main_processamento.py # pipeline de transformação e indicadores
```

Até a Fase 1, este repositório e o `dashboard-quadrantes` eram separados, e já haviam divergido em código e em dados. Foram consolidados aqui.

## Ambiente

Requer [uv](https://docs.astral.sh/uv/) e Python 3.12.

```bash
make setup     # cria o ambiente a partir do uv.lock
make test      # roda a suíte
make dashboard # sobe o dashboard local em http://localhost:8501
```

`pyproject.toml` + `uv.lock` são a fonte da verdade das dependências. O `requirements.txt` é **gerado** (`make requirements`) e existe apenas porque o Streamlit Cloud não lê `pyproject.toml` — o CI falha se ele sair de sincronia.

## Pipeline

```bash
uv run python main_coleta.py         # baixa dados brutos para data/raw/
uv run python main_processamento.py  # calcula indicadores -> dashboard/data/resultados.csv
```

`data/` não é versionado. A coleta completa de tramitações e temas ainda é cara — o redesenho está previsto na Fase 1.

## Testes

Testes são requisito de produto, não item opcional: a credibilidade do projeto depende de qualquer número exibido ser reproduzível até o dado bruto. A cobertura é organizada em quatro frentes — unitários da regra de negócio, qualidade de dados, contrato com a API da Câmara, e regressão dos indicadores publicados. Nenhum teste depende de rede.

```bash
make test
```

O CI roda a suíte a cada push.

## O viés deste projeto

Não existe métrica neutra de trabalho legislativo. Escolher o que conta como produção é uma decisão de valor, e ela foi tomada por uma pessoa: os pesos por tipo de proposição em [`legisdata/static/mapa_pesos_proposicoes.csv`](legisdata/static/mapa_pesos_proposicoes.csv) não vêm de tabela oficial nem de consenso acadêmico. São juízo do autor.

O viés declarado é a **democracia e a transparência**: o gasto público deve ser rastreável, a metodologia deve ser auditável até o dado bruto, e quem discordar dos pesos precisa conseguir abrir o arquivo, trocá-los e refazer a conta.

Apresentar um índice como objetivo seria esconder as decisões tomadas para construí-lo. Por isso o projeto não entrega veredito sobre parlamentar nenhum: entrega um instrumento e a lista do que ele não consegue ver.

## Limitações conhecidas

Além das limitações metodológicas declaradas no PRD (o projeto não mede ética, conduta nem qualidade legislativa), estas são as que afetam qualquer número exibido hoje:

- **Quem entra no ranking é decidido pelo estado de hoje, não pelo período medido.** A padronização filtra por `situacao == "Exercício"` sobre o `ultimoStatus` da API. Dos 647 parlamentares que exerceram mandato na 57ª legislatura, 508 estão no artefato publicado: os outros 139 produziram durante o período e não aparecem, porque hoje não ocupam a cadeira.
- **Mandato parcial é comparado com mandato inteiro.** Não há normalização por tempo de exercício. Quem assumiu como suplente, saiu para cargo no Executivo ou voltou à cadeira no meio da legislatura é medido contra quem serviu os quatro anos, tanto em produtividade quanto em gasto.
- **As métricas de eficácia de tramitação refletem a data da coleta, não o estado atual.** É o mesmo defeito de reprocessamento que congelava o gasto CEAP, descrito em [qualidade dos dados](docs/qualidade_dados.md); o gasto foi corrigido, a tramitação não.
- **O pipeline calcula um ranking composto (produtividade + gasto), mas o dashboard publica produtividade pura.** Compor os dois eixos numa nota única exigiria arbitrar quanto um real vale em proposição, e a decisão está adiada para a Fase 2. O dashboard declara qual dos dois está exibindo.

Elas estão declaradas também na própria interface: quem abre o dashboard lê as ressalvas antes de ler o ranking.

Uma limitação que **saiu** desta lista: gasto CEAP implausivelmente baixo. Foi investigado, e o caso extremo (R$ 22,04 no ajustado) é real — o parlamentar só usa a cota para passagem aérea, que o ajuste remove. A causa de fundo, um artefato calculado sobre fonte obsoleta, foi corrigida e hoje o gasto publicado bate com a fonte deputado a deputado. O registro está em [qualidade dos dados](docs/qualidade_dados.md).

## Licença

Ainda não definida — é questão em aberto no PRD, para código e para dados.

## Autor

[Aurelius Oliveira](https://github.com/aureliusoliveira)
