# Quadrantes da Produtividade Legislativa

Plataforma pública e contínua que cruza **custo de mandato** (CEAP) e **produtividade legislativa** de deputados federais brasileiros, a partir dos dados abertos da Câmara. Classifica os parlamentares em quatro quadrantes e publica um ranking com metodologia aberta e auditável.

**Usuário primário:** jornalista de dados.
**Cadência:** mensal. **Escopo:** plataforma contínua, com legislatura como dimensão.

O escopo, os não-objetivos e as fases estão no [PRD](docs/quadrantes_prd_v1.md).

> **Estado atual: Fase 1 (Fundação), em andamento.** Há divergências conhecidas entre a metodologia documentada e a implementada, e valores de gasto CEAP sob investigação. Veja [Limitações conhecidas](#limitações-conhecidas) antes de citar qualquer número.

## Estrutura

```
├── legisdata/            # coleta e cálculo de indicadores
│   ├── coleta/           # coletores por fonte (API da Câmara, arquivos CEAP)
│   ├── processamento/    # carregamento e padronização das bases
│   ├── indicadores/      # regra de negócio: produtividade, gastos, tramitação, temas
│   └── config.py
├── dashboard/            # app Streamlit (entrypoint do Streamlit Cloud)
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

## Limitações conhecidas

Além das limitações metodológicas declaradas no PRD (o projeto não mede ética, conduta nem qualidade legislativa), há problemas em aberto sendo tratados na Fase 1:

- O ranking exibido no dashboard é de produtividade pura, enquanto o texto da página descreve uma composição de dois critérios.
- Alguns deputados aparecem com gasto CEAP implausivelmente baixo, o que empurra dado ausente para o topo do ranking.
- As métricas de eficácia de tramitação refletem a data da primeira coleta, não o estado atual.

## Licença

Ainda não definida — é questão em aberto no PRD, para código e para dados.

## Autor

[Aurelius Oliveira](https://github.com/aureliusoliveira)
