"""Cálculos dos indicadores definidos na etapa 6 do notebook."""
# [IA] registro 22
import numpy as np
import pandas as pd

MIN_DISPATCH_ORDERS = 20
MIN_REVIEW_ORDERS = 10
HIGH_DELAY_RATE_PCT = 20
HIGH_LOW_REVIEW_RATE_PCT = 20


def filter_data(d, states, categories, sellers, start, end):
    mask = pd.Series(True, index=d.index)
    if states:
        mask &= d["seller_state"].isin(states)
    if sellers:
        mask &= d["seller_id"].isin(sellers)
    if categories:
        selected = set(categories)
        category_match = d["categorias"].fillna("").str.split("|", regex=False).map(
            lambda values: bool(selected.intersection(values))
        )
        mask &= category_match
    dates = pd.to_datetime(d["order_purchase_timestamp"], errors="coerce")
    if start is not None:
        mask &= dates.ge(pd.Timestamp(start))
    if end is not None:
        mask &= dates.lt(pd.Timestamp(end) + pd.Timedelta(days=1))
    return d.loc[mask].copy()


def seller_metrics(d):
    base = d.groupby("seller_id", as_index=False).agg(
        seller_state=("seller_state", "first"),
        seller_city=("seller_city", "first"),
        qtd_pedidos=("order_id", "nunique"),
    )

    eligible = d.loc[d["despacho_avaliavel"].fillna(False)].copy()
    eligible["pedido_atrasado"] = eligible["flag_atraso_despacho"].fillna(False)
    dispatch = eligible.groupby("seller_id").agg(
        pedidos_despacho_avaliavel=("order_id", "size"),
        pedidos_com_atraso_despacho=("pedido_atrasado", "sum"),
        atraso_medio_despacho_dias=("atraso_despacho_dias", "mean"),
    )

    reviewed = d.loc[d["nota_media_pedido"].notna()].copy()
    reviewed["pedido_nota_baixa"] = reviewed["nota_media_pedido"].le(2)
    reviews = reviewed.groupby("seller_id").agg(
        pedidos_com_nota=("order_id", "size"),
        nota_media=("nota_media_pedido", "mean"),
        pedidos_nota_baixa=("pedido_nota_baixa", "sum"),
    )

    metrics = base.join(dispatch, on="seller_id").join(reviews, on="seller_id")
    for column in (
        "pedidos_despacho_avaliavel",
        "pedidos_com_atraso_despacho",
        "pedidos_com_nota",
        "pedidos_nota_baixa",
    ):
        metrics[column] = metrics[column].fillna(0).astype(int)
    metrics["taxa_atraso_despacho_pct"] = (
        100
        * metrics["pedidos_com_atraso_despacho"]
        / metrics["pedidos_despacho_avaliavel"].replace(0, np.nan)
    )
    metrics["taxa_nota_baixa_pct"] = (
        100
        * metrics["pedidos_nota_baixa"]
        / metrics["pedidos_com_nota"].replace(0, np.nan)
    )
    return metrics


def delay_ranking(metrics):
    ranked = metrics.loc[
        metrics["pedidos_despacho_avaliavel"].ge(MIN_DISPATCH_ORDERS)
    ]
    return ranked.sort_values(
        ["taxa_atraso_despacho_pct", "seller_id"],
        ascending=[False, True],
        na_position="last",
    )


def review_comparison(d):
    reviewed = d.loc[
        d["nota_media_pedido"].notna() & d["flag_atraso_despacho"].notna()
    ].copy()
    reviewed["pedido_nota_baixa"] = reviewed["nota_media_pedido"].le(2)
    comparison = reviewed.groupby("flag_atraso_despacho").agg(
        qtd_pedidos=("order_id", "size"),
        nota_media=("nota_media_pedido", "mean"),
        taxa_nota_baixa_pct=("pedido_nota_baixa", "mean"),
    )
    comparison["taxa_nota_baixa_pct"] *= 100
    comparison = comparison.reindex([True, False]).rename(
        index={True: "Com atraso no despacho", False: "Sem atraso no despacho"}
    )
    comparison.index.name = "situacao"
    return comparison.reset_index()


def monitoring_metrics(d):
    metrics = seller_metrics(d)
    eligible = metrics.loc[
        metrics["pedidos_despacho_avaliavel"].ge(MIN_DISPATCH_ORDERS)
        & metrics["pedidos_com_nota"].ge(MIN_REVIEW_ORDERS)
    ].copy()
    high_delay = eligible["taxa_atraso_despacho_pct"].ge(HIGH_DELAY_RATE_PCT)
    high_low_reviews = eligible["taxa_nota_baixa_pct"].ge(
        HIGH_LOW_REVIEW_RATE_PCT
    )
    eligible["classificacao"] = "Acompanhamento regular"
    eligible.loc[high_delay | high_low_reviews, "classificacao"] = "Advertência"
    eligible.loc[high_delay & high_low_reviews, "classificacao"] = (
        "Revisão prioritária"
    )
    return eligible.sort_values(
        ["classificacao", "taxa_atraso_despacho_pct", "taxa_nota_baixa_pct"],
        ascending=[True, False, False],
    )
