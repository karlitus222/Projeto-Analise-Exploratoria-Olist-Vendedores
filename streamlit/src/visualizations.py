"""Gráficos interativos dos indicadores da etapa 6."""
# [IA] registro 15
import altair as alt

from .presentation import seller_label


def ranking_chart(metrics):
    data = metrics.head(12).copy()
    data["vendedor"] = data.apply(seller_label, axis=1)
    data["taxa_atraso"] = data["taxa_atraso_despacho_pct"]
    selection = alt.selection_point(fields=["seller_id"], name="vendedor_destacado")
    base = alt.Chart(data).encode(
        x=alt.X(
            "taxa_atraso:Q",
            title="Pedidos com atraso (%)",
            scale=alt.Scale(domain=[0, 100]),
        ),
        y=alt.Y("vendedor:N", title="Vendedor (município e ID)", sort="-x"),
        tooltip=[
            alt.Tooltip("vendedor:N", title="Vendedor"),
            alt.Tooltip("seller_id:N", title="ID completo"),
            alt.Tooltip(
                "pedidos_com_atraso_despacho:Q", title="Pedidos com atraso"
            ),
            alt.Tooltip(
                "pedidos_despacho_avaliavel:Q", title="Pedidos avaliáveis"
            ),
            alt.Tooltip("taxa_atraso:Q", title="Taxa de atraso (%)", format=".2f"),
        ],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.35)),
    )
    return (
        (base.mark_bar(color="#087F8C") + base.mark_point(color="#087F8C", size=90))
        .add_params(selection)
        .properties(height=300)
        .interactive(bind_y=False)
    )


def review_chart(comparison):
    data = comparison.dropna(subset=["nota_media"]).copy()
    selection = alt.selection_point(fields=["situacao"], name="grupo_destacado")
    return (
        alt.Chart(data)
        .mark_bar(size=70)
        .encode(
            x=alt.X("situacao:N", title="Situação do despacho"),
            y=alt.Y(
                "nota_media:Q",
                title="Nota média por pedido",
                scale=alt.Scale(domain=[0, 5]),
            ),
            color=alt.Color(
                "situacao:N",
                title="Situação",
                scale=alt.Scale(
                    domain=["Sem atraso no despacho", "Com atraso no despacho"],
                    range=["#087F8C", "#E58F37"],
                ),
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.35)),
            tooltip=[
                alt.Tooltip("situacao:N", title="Situação"),
                alt.Tooltip("qtd_pedidos:Q", title="Pedidos avaliados"),
                alt.Tooltip("nota_media:Q", title="Nota média", format=".2f"),
                alt.Tooltip(
                    "taxa_nota_baixa_pct:Q", title="Notas 1 ou 2 (%)", format=".2f"
                ),
            ],
        )
        .add_params(selection)
        .properties(height=300)
        .interactive(bind_x=False)
    )


def criteria_chart(monitored):
    counts = (
        monitored["classificacao"]
        .value_counts()
        .rename_axis("classificacao")
        .reset_index(name="vendedores")
    )
    selection = alt.selection_point(
        fields=["classificacao"], name="criterio_destacado"
    )
    return (
        alt.Chart(counts)
        .mark_bar(color="#087F8C")
        .encode(
            x=alt.X("vendedores:Q", title="Quantidade de vendedores"),
            y=alt.Y(
                "classificacao:N",
                title="Resultado dos critérios",
                sort=[
                    "Revisão prioritária",
                    "Advertência",
                    "Acompanhamento regular",
                ],
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.35)),
            tooltip=[
                alt.Tooltip("classificacao:N", title="Classificação"),
                alt.Tooltip("vendedores:Q", title="Vendedores"),
            ],
        )
        .add_params(selection)
        .properties(height=190)
        .interactive(bind_y=False)
    )
