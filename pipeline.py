"""Pipeline de pré-processamento do Briefing 5 da Olist.

Recebe os cinco DataFrames brutos do projeto e gera uma tabela analítica em
que cada linha representa um vendedor dentro de um pedido.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


# [IA] registro 3
def _conferir_chave(df: pd.DataFrame, colunas: list[str], nome: str) -> None:
    """Garante que uma chave esteja preenchida e não possua repetições."""
    if df[colunas].isna().any().any():
        raise ValueError(f"{nome}: há valores ausentes na chave {colunas}.")
    if df.duplicated(colunas).any():
        raise ValueError(f"{nome}: há chaves repetidas em {colunas}.")


# [IA] registro 2
def _copiar_e_remover_duplicatas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria uma cópia do DataFrame e remove somente linhas inteiramente iguais."""
    return df.copy().drop_duplicates().copy()


# [IA] registro 2
def relacionar_tabelas(
    orders: pd.DataFrame,
    items: pd.DataFrame,
    products: pd.DataFrame,
    sellers: pd.DataFrame,
    reviews: pd.DataFrame,
) -> pd.DataFrame:
    """Relaciona as bases sem multiplicar as linhas de itens.

    As avaliações são resumidas por pedido antes da junção, pois há pedidos
    com mais de uma avaliação no conjunto de dados original.
    """
    orders = _copiar_e_remover_duplicatas(orders)
    items = _copiar_e_remover_duplicatas(items)
    products = _copiar_e_remover_duplicatas(products)
    sellers = _copiar_e_remover_duplicatas(sellers)
    reviews = _copiar_e_remover_duplicatas(reviews)

    _conferir_chave(orders, ["order_id"], "orders")
    _conferir_chave(items, ["order_id", "order_item_id"], "items")
    _conferir_chave(products, ["product_id"], "products")
    _conferir_chave(sellers, ["seller_id"], "sellers")

    for coluna in ["order_id", "seller_id", "product_id"]:
        if items[coluna].isna().any():
            raise ValueError(f"items: há valores ausentes em {coluna}.")

    colunas_datas_orders = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for coluna in colunas_datas_orders:
        orders[coluna] = pd.to_datetime(orders[coluna], errors="coerce")
    items["shipping_limit_date"] = pd.to_datetime(
        items["shipping_limit_date"], errors="coerce"
    )

    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
    reviews["nota_valida"] = reviews["review_score"].where(
        reviews["review_score"].isin([1, 2, 3, 4, 5])
    )
    reviews["nota_baixa"] = reviews["nota_valida"].le(2) & reviews["nota_valida"].notna()

    avaliacoes = reviews.dropna(subset=["order_id"]).groupby(
        "order_id", as_index=False
    ).agg(
        qtd_avaliacoes_pedido=("review_id", "size"),
        qtd_avaliacoes_validas=("nota_valida", "count"),
        nota_media_pedido=("nota_valida", "mean"),
        menor_nota_pedido=("nota_valida", "min"),
        maior_nota_pedido=("nota_valida", "max"),
        qtd_avaliacoes_baixas_pedido=("nota_baixa", "sum"),
    )
    _conferir_chave(avaliacoes, ["order_id"], "avaliações agregadas")

    base_itens = items.copy()
    base_itens["qtd_vendedores_pedido"] = base_itens["order_id"].map(
        items.groupby("order_id")["seller_id"].nunique()
    )

    for direita, chave, indicador in [
        (orders, "order_id", "pedido_encontrado"),
        (products, "product_id", "produto_encontrado"),
        (sellers, "seller_id", "vendedor_encontrado"),
        (avaliacoes, "order_id", "avaliacao_encontrada"),
    ]:
        total_antes = len(base_itens)
        base_itens = base_itens.merge(
            direita,
            on=chave,
            how="left",
            validate="many_to_one",
            indicator=True,
        )
        base_itens[indicador] = base_itens["_merge"].eq("both")
        base_itens = base_itens.drop(columns="_merge")
        if len(base_itens) != total_antes:
            raise ValueError("Uma junção alterou a quantidade de itens.")

    _conferir_chave(base_itens, ["order_id", "order_item_id"], "itens relacionados")
    return base_itens


# [IA] registro 2
def construir_tabela_analitica(base_itens: pd.DataFrame) -> pd.DataFrame:
    """Gera uma linha para cada combinação de vendedor e pedido."""
    itens = base_itens.copy()
    compra = itens["order_purchase_timestamp"]
    despacho = itens["order_delivered_carrier_date"]
    prazo = itens["shipping_limit_date"]

    itens["despacho_antes_compra"] = despacho.notna() & compra.notna() & despacho.lt(compra)
    itens["prazo_antes_compra"] = prazo.notna() & compra.notna() & prazo.lt(compra)
    itens["prazo_item_valido"] = compra.notna() & prazo.notna() & prazo.ge(compra)
    itens["item_despacho_avaliavel"] = (
        itens["prazo_item_valido"]
        & despacho.notna()
        & despacho.ge(compra)
        & itens["pedido_encontrado"]
        & ~itens["order_status"].isin(["canceled", "unavailable"])
    )
    itens["item_atrasado"] = itens["item_despacho_avaliavel"] & despacho.gt(prazo)
    itens["categoria_analise"] = itens["product_category_name"].fillna("sem_categoria")

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
            "valor_produtos": ("price", "sum"),
            "valor_frete": ("freight_value", "sum"),
            "prazo_despacho_vendedor": ("shipping_limit_date", "min"),
            "ultimo_prazo_despacho_vendedor": ("shipping_limit_date", "max"),
            "qtd_itens_prazo_valido": ("prazo_item_valido", "sum"),
            "qtd_itens_despacho_avaliavel": ("item_despacho_avaliavel", "sum"),
            "qtd_itens_atrasados": ("item_atrasado", "sum"),
            "qtd_itens_sem_produto": ("produto_encontrado", lambda serie: (~serie).sum()),
            "qtd_categorias": ("categoria_analise", "nunique"),
            "categorias": ("categoria_analise", lambda serie: "|".join(sorted(serie.unique()))),
            "despacho_antes_compra": ("despacho_antes_compra", "max"),
            "prazo_antes_compra": ("prazo_antes_compra", "max"),
        }
    )
    tabela = itens.groupby(["seller_id", "order_id"], as_index=False).agg(**agregacoes)

    tabela["valor_total"] = tabela["valor_produtos"] + tabela["valor_frete"]
    tabela["pedido_multivendedor"] = tabela["qtd_vendedores_pedido"].gt(1)
    tabela["mes_compra"] = tabela["order_purchase_timestamp"].dt.strftime("%Y-%m")
    tabela["despacho_avaliavel"] = tabela["qtd_itens_despacho_avaliavel"].eq(
        tabela["qtd_itens"]
    )
    tabela["diferenca_despacho_dias"] = (
        tabela["order_delivered_carrier_date"] - tabela["prazo_despacho_vendedor"]
    ).dt.total_seconds().div(86400).where(tabela["despacho_avaliavel"])
    tabela["atraso_despacho_dias"] = tabela["diferenca_despacho_dias"].clip(lower=0)
    tabela["flag_atraso_despacho"] = tabela["diferenca_despacho_dias"].gt(0).astype("boolean")
    tabela.loc[~tabela["despacho_avaliavel"], "flag_atraso_despacho"] = pd.NA

    entrega = tabela["order_delivered_customer_date"]
    estimativa = tabela["order_estimated_delivery_date"]
    tabela["entrega_avaliavel"] = (
        tabela["order_status"].eq("delivered")
        & entrega.notna()
        & estimativa.notna()
        & tabela["order_purchase_timestamp"].notna()
        & entrega.ge(tabela["order_purchase_timestamp"])
        & estimativa.ge(tabela["order_purchase_timestamp"].dt.normalize())
    )
    tabela["diferenca_entrega_dias"] = (
        entrega.dt.normalize() - estimativa.dt.normalize()
    ).dt.days.where(tabela["entrega_avaliavel"])
    tabela["atraso_entrega_dias"] = tabela["diferenca_entrega_dias"].clip(lower=0)
    tabela["flag_atraso_entrega"] = tabela["diferenca_entrega_dias"].gt(0).astype("boolean")
    tabela.loc[~tabela["entrega_avaliavel"], "flag_atraso_entrega"] = pd.NA

    tabela["flag_nota_baixa"] = tabela["nota_media_pedido"].le(2).astype("boolean")
    tabela.loc[tabela["nota_media_pedido"].isna(), "flag_nota_baixa"] = pd.NA

    _conferir_chave(tabela, ["seller_id", "order_id"], "tabela analítica")
    return tabela


# [IA] registro 2
def resumir_vendedores(tabela_analitica: pd.DataFrame) -> pd.DataFrame:
    """Calcula os indicadores usados nas três perguntas do Briefing 5."""
    resumo = tabela_analitica.groupby("seller_id", as_index=False).agg(
        seller_state=("seller_state", "first"),
        qtd_pedidos=("order_id", "nunique"),
        pedidos_despacho_avaliavel=("despacho_avaliavel", "sum"),
        pedidos_com_atraso_despacho=("flag_atraso_despacho", "sum"),
        atraso_medio_despacho_dias=("atraso_despacho_dias", "mean"),
        pedidos_com_nota=("nota_media_pedido", "count"),
        nota_media=("nota_media_pedido", "mean"),
        pedidos_nota_baixa=("flag_nota_baixa", "sum"),
    )
    resumo["taxa_atraso_despacho_pct"] = 100 * resumo[
        "pedidos_com_atraso_despacho"
    ] / resumo["pedidos_despacho_avaliavel"].replace(0, float("nan"))
    resumo["taxa_nota_baixa_pct"] = 100 * resumo["pedidos_nota_baixa"] / resumo[
        "pedidos_com_nota"
    ].replace(0, float("nan"))
    return resumo


# [IA] registro 2
def preprocessar(
    orders: pd.DataFrame,
    items: pd.DataFrame,
    products: pd.DataFrame,
    sellers: pd.DataFrame,
    reviews: pd.DataFrame,
    pasta_saida: str | Path = Path.cwd(),
) -> pd.DataFrame:
    """Executa o pré-processamento e salva os CSVs em tabelas_analiticas."""
    base_itens = relacionar_tabelas(orders, items, products, sellers, reviews)
    tabela_analitica = construir_tabela_analitica(base_itens)

    pasta_tabelas = Path(pasta_saida) / "tabelas_analiticas"
    pasta_tabelas.mkdir(parents=True, exist_ok=True)

    tabela_analitica.to_csv(
        pasta_tabelas / "tabela_vendedor_pedido.csv",
        index=False,
        encoding="utf-8-sig",
    )
    resumir_vendedores(tabela_analitica).to_csv(
        pasta_tabelas / "resumo_vendedores.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return tabela_analitica
