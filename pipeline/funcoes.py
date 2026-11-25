import pandas as pd


COLUNAS_DATA = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


def limpar_dados(dados_brutos):
    # Copia as bases, remove linhas iguais e prepara datas e notas.
    dados = {
        nome: df.drop_duplicates().copy()
        for nome, df in dados_brutos.items()
    }

    for tabela, colunas in COLUNAS_DATA.items():
        for coluna in colunas:
            if coluna in dados[tabela].columns:
                dados[tabela][coluna] = pd.to_datetime(
                    dados[tabela][coluna],
                    errors="coerce",
                )

    dados["reviews"]["review_score"] = pd.to_numeric(
        dados["reviews"]["review_score"],
        errors="coerce",
    )
    # [IA] registro 2
    return dados


def relacionar_tabelas(dados):
    # Junta as bases usando os itens como tabela principal.
    orders = dados["orders"]
    items = dados["items"]
    products = dados["products"]
    sellers = dados["sellers"]
    reviews = dados["reviews"]

    # [IA] registro 2
    chaves_dos_itens = ["order_id", "order_item_id", "product_id", "seller_id"]
    if items[chaves_dos_itens].isna().any().any():
        raise ValueError("A tabela items tem identificadores vazios.")
    if items.duplicated(["order_id", "order_item_id"]).any():
        raise ValueError("A tabela items tem itens repetidos no mesmo pedido.")

    reviews["nota_valida"] = reviews["review_score"].where(
        reviews["review_score"].isin([1, 2, 3, 4, 5])
    )
    reviews["nota_baixa"] = (
        reviews["nota_valida"].le(2) & reviews["nota_valida"].notna()
    )
    avaliacoes = (
        reviews.dropna(subset=["order_id"])
        .groupby("order_id", as_index=False)
        .agg(
            qtd_avaliacoes_pedido=("review_id", "size"),
            qtd_avaliacoes_validas=("nota_valida", "count"),
            nota_media_pedido=("nota_valida", "mean"),
            menor_nota_pedido=("nota_valida", "min"),
            maior_nota_pedido=("nota_valida", "max"),
            qtd_avaliacoes_baixas_pedido=("nota_baixa", "sum"),
        )
    )

    base = items.copy()
    base["qtd_vendedores_pedido"] = base.groupby("order_id")[
        "seller_id"
    ].transform("nunique")
    base = base.merge(
        orders, on="order_id", how="left", validate="many_to_one",
        indicator="pedido_encontrado",
    )
    base = base.merge(
        products, on="product_id", how="left", validate="many_to_one",
        indicator="produto_encontrado",
    )
    base = base.merge(
        sellers, on="seller_id", how="left", validate="many_to_one",
        indicator="vendedor_encontrado",
    )
    base = base.merge(
        avaliacoes, on="order_id", how="left", validate="many_to_one",
        indicator="avaliacao_encontrada",
    )

    for coluna in [
        "pedido_encontrado",
        "produto_encontrado",
        "vendedor_encontrado",
        "avaliacao_encontrada",
    ]:
        base[coluna] = base[coluna].eq("both")

    return base

# [IA] registro 2

def construir_tabela_analitica(base):
    # Agrupa os itens para deixar uma linha por vendedor e pedido.
    itens = base.copy()
    compra = itens["order_purchase_timestamp"]
    despacho = itens["order_delivered_carrier_date"]
    prazo = itens["shipping_limit_date"]

    itens["despacho_antes_compra"] = despacho.notna() & despacho.lt(compra)
    itens["prazo_antes_compra"] = prazo.notna() & prazo.lt(compra)
    itens["prazo_item_valido"] = prazo.notna() & prazo.ge(compra)
    itens["prazo_item_analise"] = prazo.where(itens["prazo_item_valido"])
    itens["item_despacho_avaliavel"] = (
        itens["prazo_item_valido"]
        & despacho.notna()
        & despacho.ge(compra)
        & itens["pedido_encontrado"]
        & ~itens["order_status"].isin(["canceled", "unavailable"])
    )
    itens["item_atrasado"] = (
        itens["item_despacho_avaliavel"] & despacho.gt(prazo)
    )
    itens["categoria_analise"] = itens["product_category_name"].fillna(
        "sem_categoria"
    )

    campos_pedido = [
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "seller_city",
        "seller_state",
        "qtd_vendedores_pedido",
        "nota_media_pedido",
        "menor_nota_pedido",
        "maior_nota_pedido",
        "qtd_avaliacoes_pedido",
        "qtd_avaliacoes_validas",
        "qtd_avaliacoes_baixas_pedido",
        "pedido_encontrado",
        "vendedor_encontrado",
        "avaliacao_encontrada",
    ]
    agregacoes = {campo: (campo, "first") for campo in campos_pedido}
    agregacoes.update(
        {
            "qtd_itens": ("order_item_id", "size"),
            "qtd_produtos_distintos": ("product_id", "nunique"),
            "valor_produtos": ("price", lambda serie: serie.sum(min_count=1)),
            "valor_frete": (
                "freight_value",
                lambda serie: serie.sum(min_count=1),
            ),
            "prazo_despacho_vendedor": ("prazo_item_analise", "min"),
            "ultimo_prazo_despacho_vendedor": ("prazo_item_analise", "max"),
            "qtd_itens_prazo_valido": ("prazo_item_valido", "sum"),
            "qtd_itens_despacho_avaliavel": (
                "item_despacho_avaliavel",
                "sum",
            ),
            "qtd_itens_atrasados": ("item_atrasado", "sum"),
            "qtd_itens_sem_produto": (
                "produto_encontrado",
                lambda serie: (~serie).sum(),
            ),
            "qtd_categorias": ("categoria_analise", "nunique"),
            "categorias": (
                "categoria_analise",
                lambda serie: "|".join(sorted(serie.unique())),
            ),
            "despacho_antes_compra": ("despacho_antes_compra", "max"),
            "prazo_antes_compra": ("prazo_antes_compra", "max"),
        }
    )
    tabela = itens.groupby(
        ["seller_id", "order_id"], as_index=False
    ).agg(**agregacoes)

    tabela["valor_total"] = tabela["valor_produtos"] + tabela["valor_frete"]
    tabela["pedido_multivendedor"] = tabela["qtd_vendedores_pedido"].gt(1)
    tabela["mes_compra"] = tabela["order_purchase_timestamp"].dt.strftime("%Y-%m")

    tabela["despacho_avaliavel"] = tabela["qtd_itens_despacho_avaliavel"].eq(
        tabela["qtd_itens"]
    )
    diferenca_despacho = (
        tabela["order_delivered_carrier_date"]
        - tabela["prazo_despacho_vendedor"]
    ).dt.total_seconds() / 86400
    tabela["diferenca_despacho_dias"] = diferenca_despacho.where(
        tabela["despacho_avaliavel"]
    )
    tabela["atraso_despacho_dias"] = tabela[
        "diferenca_despacho_dias"
    ].clip(lower=0)
    tabela["flag_atraso_despacho"] = tabela["qtd_itens_atrasados"].gt(
        0
    ).astype("boolean")
    tabela.loc[~tabela["despacho_avaliavel"], "flag_atraso_despacho"] = pd.NA

    entrega = tabela["order_delivered_customer_date"]
    estimativa = tabela["order_estimated_delivery_date"]
    tabela["entrega_avaliavel"] = (
        tabela["order_status"].eq("delivered")
        & entrega.notna()
        & estimativa.notna()
        & entrega.ge(tabela["order_purchase_timestamp"])
        & estimativa.ge(tabela["order_purchase_timestamp"].dt.normalize())
    )
    tabela["diferenca_entrega_dias"] = (
        entrega.dt.normalize() - estimativa.dt.normalize()
    ).dt.days.where(tabela["entrega_avaliavel"])
    tabela["atraso_entrega_dias"] = tabela[
        "diferenca_entrega_dias"
    ].clip(lower=0)
    tabela["flag_atraso_entrega"] = tabela[
        "diferenca_entrega_dias"
    ].gt(0).astype("boolean")
    tabela.loc[~tabela["entrega_avaliavel"], "flag_atraso_entrega"] = pd.NA

    tabela["flag_nota_baixa"] = tabela["nota_media_pedido"].le(2).astype(
        "boolean"
    )
    tabela.loc[tabela["nota_media_pedido"].isna(), "flag_nota_baixa"] = pd.NA
    return tabela

# [IA] registro 2
def resumir_vendedores(tabela):
    # Calcula os indicadores principais para cada vendedor.
    resumo = tabela.groupby("seller_id", as_index=False).agg(
        seller_state=("seller_state", "first"),
        qtd_pedidos=("order_id", "nunique"),
        qtd_itens=("qtd_itens", "sum"),
        pedidos_despacho_avaliavel=("despacho_avaliavel", "sum"),
        pedidos_com_atraso_despacho=("flag_atraso_despacho", "sum"),
        atraso_medio_despacho_dias=("atraso_despacho_dias", "mean"),
        pedidos_com_nota=("nota_media_pedido", "count"),
        nota_media=("nota_media_pedido", "mean"),
        pedidos_nota_baixa=("flag_nota_baixa", "sum"),
        pedidos_multivendedor=("pedido_multivendedor", "sum"),
    )
    resumo["taxa_atraso_despacho_pct"] = (
        100
        * resumo["pedidos_com_atraso_despacho"]
        / resumo["pedidos_despacho_avaliavel"].replace(0, float("nan"))
    )
    resumo["taxa_nota_baixa_pct"] = (
        100
        * resumo["pedidos_nota_baixa"]
        / resumo["pedidos_com_nota"].replace(0, float("nan"))
    )
    return resumo
