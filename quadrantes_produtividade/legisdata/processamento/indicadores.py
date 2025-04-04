import os
import pandas as pd


class IndicadoresParlamentares:
    def __init__(self, dados: dict, caminho_pesos: str = None):
        self.deputados = dados["deputados"]
        self.proposicoes = dados["proposicoes"]
        self.autores = dados["autores"]
        self.gastos = dados["gastos"]
        self.tramitacoes = dados["tramitacoes"]
        self.temas = dados["temas"]

        self.caminho_pesos = caminho_pesos or os.path.join("legisdata", "static", "mapa_pesos_proposicoes.csv")

        self._adicionar_autores()
        self._mapear_pesos()
        self._calcular_indicadores()
        self._adicionar_tramitacoes()
        self._adicionar_temas()
        self._juntar_resultados()

    def _adicionar_autores(self):
        self.proposicoes = self.proposicoes.merge(
            self.autores,
            left_on="id", right_on="idProposicao", how="left"
        )

    def _mapear_pesos(self):
        try:
            mapa = pd.read_csv(self.caminho_pesos, sep=';')
            mapa_dict = dict(zip(mapa["siglaTipo"], mapa["peso"]))
            self.proposicoes["peso"] = self.proposicoes["siglaTipo"].map(mapa_dict).fillna(0)
        except Exception as e:
            raise ValueError(f"Erro ao carregar o mapa de pesos: {e}")

    def _calcular_indicadores(self):
        self.ind_produtividade = (
            self.proposicoes
            .groupby("idDeputado")["peso"]
            .sum()
            .reset_index()
            .rename(columns={"peso": "produtividade_legislativa"})
        )

        # Remove passagens com origem OU destino em Brasília (a critério já acordado)
        gastos_filtrados = self.gastos[
            ~self.gastos["txtDescricao"].str.contains("PASSAGE", case=False, na=False)
            | ~self.gastos["txtTrecho"].str.contains("BSB", case=False, na=False)
        ]
        
        self.ind_gastos = (
            gastos_filtrados
            .groupby(["idDeputado", "sgUF", "sgPartido"])["vlrLiquido"]
            .sum()
            .reset_index()
            .rename(columns={"vlrLiquido": "gasto_ceap_ajustado"})
        )

    def _classificar_tramitacao(self, situacao: str) -> str:
        if not isinstance(situacao, str):
            return "andamento"
        situacao = situacao.lower()
        if "norma jurídica" in situacao or "sanção" in situacao or "promulgação" in situacao or "senado" in situacao:
            return "sucesso"
        if "arquivada" in situacao or "retirado" in situacao or "prejudic" in situacao or "devolvida" in situacao or "recusado" in situacao:
            return "fracasso"
        return "andamento"

    def _adicionar_tramitacoes(self):
        if self.tramitacoes is None:
            return

        df = self.proposicoes.merge(
            self.tramitacoes,
            left_on="id", right_on="idProposicao", how="left"
        )
        df = df[["idDeputado", "descricaoSituacao"]].dropna()
        df["categoriaSituacao"] = df["descricaoSituacao"].apply(self._classificar_tramitacao)

        df_pct = (
            df.groupby("idDeputado")["categoriaSituacao"]
            .value_counts(normalize=True)
            .unstack(fill_value=0)
            .reset_index()
            .rename(columns={
                "sucesso": "pct_sucesso",
                "fracasso": "pct_fracasso",
                "andamento": "pct_andamento"
            })
        )

        self.ind_tramitacao = df_pct

    def _adicionar_temas(self):
        if self.temas is None:
            return

        df = self.proposicoes.merge(
            self.temas,
            left_on="id", right_on="idProposicao", how="inner"
        )

        temas_por_dep = {}
        for dep_id, grupo in df.groupby("idDeputado"):
            temas_mais_comuns = (
                grupo["tema"]
                .value_counts()
                .nlargest(3)
                .index.tolist()
            )

            if len(temas_mais_comuns) == 1:
                texto = temas_mais_comuns[0]
            elif len(temas_mais_comuns) == 2:
                texto = f"{temas_mais_comuns[0]} e {temas_mais_comuns[1]}"
            elif len(temas_mais_comuns) == 3:
                texto = f"{temas_mais_comuns[0]}, {temas_mais_comuns[1]} e {temas_mais_comuns[2]}"
            else:
                texto = ""

            temas_por_dep[dep_id] = texto

        self.ind_temas = (
            pd.DataFrame.from_dict(temas_por_dep, orient="index", columns=["temas_destaque"])
            .reset_index()
            .rename(columns={"index": "idDeputado"})
        )

    def _juntar_resultados(self):
        dfs = [
            self.deputados,
            self.ind_produtividade.rename(columns={"idDeputado": "idDeputado"}),
            self.ind_gastos.rename(columns={"idDeputado": "idDeputado"}),
        ]

        if hasattr(self, "ind_tramitacao"):
            dfs.append(self.ind_tramitacao)

        if hasattr(self, "ind_temas"):
            dfs.append(self.ind_temas)

        resultado = dfs[0]
        for df in dfs[1:]:
            resultado = resultado.merge(df, on="idDeputado", how="left")

        resultado["pontuacao_legislativa"] = resultado["produtividade_legislativa"].fillna(0)

        mediana_pontuacao = resultado["pontuacao_legislativa"].median()
        mediana_gasto = resultado["gasto_ceap_ajustado"].median()

        def classificar_quadrante(row):
            if row["pontuacao_legislativa"] >= mediana_pontuacao:
                return "Alta produtividade e " + ("alto custo" if row["gasto_ceap_ajustado"] >= mediana_gasto else "baixo custo")
            else:
                return "Baixa produtividade e " + ("alto custo" if row["gasto_ceap_ajustado"] >= mediana_gasto else "baixo custo")

        resultado["quadrante"] = resultado.apply(classificar_quadrante, axis=1)
        resultado["ranking_leg"] = resultado["pontuacao_legislativa"].rank(ascending=False, method="dense").astype(int)
        resultado["ranking_gastos"] = resultado["gasto_ceap_ajustado"].rank(ascending=True, method="dense").astype(int)
        resultado["ranking_soma"] = resultado["ranking_leg"] + resultado["ranking_gastos"]
        resultado["ranking"] = resultado["ranking_soma"].rank(ascending=True, method="dense").astype(int)
        

        self.resultados = resultado

if __name__ == "__main__":
    # Exemplo de uso
    dados = {
        "deputados": pd.DataFrame({
            "idDeputado": [1, 2],
            "nome": ["Deputado A", "Deputado B"],
        }),
        "proposicoes": pd.DataFrame({
            "id": [1, 2, 3],
            "siglaTipo": ["PL", "PL", "PL"],
            "peso": [0.5, 0.7, 0.9]
        }),
        "autores": pd.DataFrame({
            "idProposicao": [1, 2, 3],
            "idDeputado": [1, 1, 2]
        }),
        "gastos": pd.DataFrame({
            "idDeputado": [1, 2],
            "sgUF": ["SP", "RJ"],
            "sgPartido": ["PT", "PSDB"],
            "vlrLiquido": [1000, 2000],
            "txtDescricao": ["GASTO A", "GASTO B"],
            "txtTrecho": ["BSB - SP", "BSB - RJ"]
        }),
        "tramitacoes": pd.DataFrame({
            "idProposicao": [1, 2],
            "descricaoSituacao": ["Arquivada", "Aprovada"]
        }),
        "temas": pd.DataFrame({
            "idProposicao": [1, 2],
            "tema": ["Tema A", "Tema B"]
        })
    }

    indicadores = IndicadoresParlamentares(dados)
    print(indicadores.resultados)
