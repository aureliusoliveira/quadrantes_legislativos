# Quadrantes da Produtividade Legislativa

Uma solução de engenharia e análise de dados que avalia a produtividade de deputados federais brasileiros ao cruzar informações de custos parlamentares com métricas de atividade legislativa. O projeto oferece um dashboard interativo que permite explorar visualmente os quadrantes de produtividade (alto/baixo custo x alta/baixa produtividade) e fornece insights estratégicos sobre o desempenho parlamentar.

## 🚀 Visão Geral

Este projeto coleta, processa e analisa dados legislativos, entregando uma visualização interativa dos resultados. Desenvolvido com foco em **engenharia de dados**, ele inclui pipelines para ingestão e transformação de dados, além de uma interface amigável para exploração analítica.

## 📂 Estrutura do Projeto

```
quadrantes_produtividade/
├── main_coleta.py            # Pipeline de coleta de dados brutos
├── main_processamento.py     # Pipeline de transformação e enriquecimento de dados
├── dashboard_interativo.py   # Inicialização do dashboard Streamlit
├── requirements.txt          # Dependências do projeto
├── dashboard/
│   ├── app.py                # Aplicação principal do dashboard
│   ├── graficos.py           # Componentes gráficos (Plotly)
│   ├── pages/                # Páginas adicionais do dashboard
│   ├── data/
│   │   └── resultados.csv    # Dados processados prontos para visualização
│   └── utils/                # Utilitários de suporte
└── checkpoints/              # Controle de arquivos já processados
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- [Streamlit](https://streamlit.io/) - Interface de visualização interativa
- [Pandas](https://pandas.pydata.org/) - Manipulação e análise de dados
- [Plotly](https://plotly.com/python/) - Visualizações ricas e interativas
- [Requests](https://docs.python-requests.org/) - Requisições HTTP para coleta de dados

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/tcc_pucrs.git
cd tcc_pucrs/quadrantes_produtividade
pip install -r requirements.txt
```

## ⚡ Uso

1. **Executar pipeline de coleta:**
   ```bash
   python main_coleta.py
   ```
2. **Executar pipeline de processamento:**
   ```bash
   python main_processamento.py
   ```
3. **Iniciar o dashboard interativo:**
   ```bash
   streamlit run dashboard_interativo.py
   ```

Acesse a aplicação no navegador em [http://localhost:8501](http://localhost:8501).

## 📊 Funcionalidades

- Visualização dos quadrantes de produtividade legislativa
- Filtros dinâmicos por partido, estado (UF) e legislatura
- Mini perfis de deputados com indicadores de atuação
- Exportação de resultados para análise externa

## 👨‍💻 Autor

[Aurelius Oliveira](https://github.com/seu-usuario)

## 📃 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 💡 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
