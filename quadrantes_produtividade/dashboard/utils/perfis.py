def gerar_mini_perfil_legislativo(id_deputado: str, dados: dict) -> str:
    df = dados["resultados"]
    dep = df[df["idDeputado"] == int(id_deputado)].iloc[0]

    nome = dep["nome"]
    partido = dep["siglaPartido"]
    uf = dep["siglaUf"]
    pontuacao = round(dep["pontuacao_legislativa"], 1)
    gasto = f"R$ {dep['gasto_ceap_ajustado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    quadrante = dep["quadrante"]
    ranking = dep["ranking"]

    resumo = (
        f"**{nome}** ({partido}-{uf}) está no quadrante **{quadrante}**, "
        f"com pontuação legislativa de **{pontuacao}** e gasto ajustado de **{gasto}**. "
        f"Atualmente ocupa a **{ranking}ª posição** no ranking geral."
    )

    return resumo


def gerar_perfil_detalhado(id_deputado: str, dados: dict) -> str:
    df = dados["resultados"]
    dep = df[df["idDeputado"] == int(id_deputado)].iloc[0]

    nome = dep["nome"]
    partido = dep["siglaPartido"]
    uf = dep["siglaUf"]
    pontuacao = round(dep["pontuacao_legislativa"], 1)
    produtividade = round(dep["produtividade_legislativa"], 1)
    gasto = f"R$ {dep['gasto_ceap_ajustado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    quadrante = dep["quadrante"]
    ranking = dep["ranking"]
    temas = dep.get("temas_destaque", "não informados")

    sucesso = f"{dep['pct_sucesso']*100:.1f}%" if not pd.isna(dep["pct_sucesso"]) else "N/D"
    fracasso = f"{dep['pct_fracasso']*100:.1f}%" if not pd.isna(dep["pct_fracasso"]) else "N/D"
    andamento = f"{dep['pct_andamento']*100:.1f}%" if not pd.isna(dep["pct_andamento"]) else "N/D"

    resumo = f"""
**📌 Deputado(a):** {nome} ({partido}-{uf})  
**📊 Quadrante:** {quadrante}  
**🥇 Ranking geral:** {ranking}º  
**📈 Pontuação legislativa:** {pontuacao}  
**⚙️ Produtividade legislativa:** {produtividade}  
**💰 Gasto ajustado com CEAP:** {gasto}

**🧾 Situação das proposições:**
- Sucesso: {sucesso}
- Fracasso: {fracasso}
- Em tramitação: {andamento}

**🏷️ Temas mais frequentes:** {temas}
"""
    return resumo
