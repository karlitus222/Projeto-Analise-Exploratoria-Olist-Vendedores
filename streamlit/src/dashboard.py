"""Interface gerencial baseada nos indicadores da etapa 6."""
# [IA] registro 22
from pathlib import Path

import pandas as pd
import streamlit as st
from .load_data import ROOT
from .analysis import (
    MIN_DISPATCH_ORDERS,
    MIN_REVIEW_ORDERS,
    filter_data,
    seller_metrics,
    delay_ranking,
    review_comparison,
    monitoring_metrics,
)
from .visualizations import ranking_chart, review_chart, criteria_chart
from .presentation import ORIGINAL_CONCLUSIONS, business_summary, seller_label

FINAL_CSV = ROOT.parent / "tabelas_analiticas" / "tabela_vendedor_pedido.csv"
ALL_STATES = "Todos os estados"
ALL_CATEGORIES = "Todas as categorias"
REQUIRED_COLUMNS = {
    "seller_id",
    "order_id",
    "seller_state",
    "seller_city",
    "categorias",
    "order_purchase_timestamp",
    "despacho_avaliavel",
    "flag_atraso_despacho",
    "atraso_despacho_dias",
    "nota_media_pedido",
}


@st.cache_data
def read_final(path, modified_ns):
    if Path(path).stat().st_mtime_ns != modified_ns:
        raise RuntimeError("O CSV final mudou durante a leitura; atualize o painel.")
    d = pd.read_csv(path, dtype={"order_id": "string", "seller_id": "string"})
    missing = REQUIRED_COLUMNS.difference(d.columns)
    if missing:
        raise ValueError(
            "O CSV final não contém as colunas necessárias: "
            + ", ".join(sorted(missing))
        )
    for column in ("despacho_avaliavel", "flag_atraso_despacho"):
        values = d[column].astype("string").str.lower()
        invalid = values.notna() & ~values.isin(["true", "false"])
        if invalid.any():
            raise ValueError(
                f"O campo {column} contém valores booleanos inválidos."
            )
        d[column] = values.map({"true": True, "false": False}).astype("boolean")
    d["nota_media_pedido"] = pd.to_numeric(
        d["nota_media_pedido"], errors="coerce"
    )
    d["atraso_despacho_dias"] = pd.to_numeric(
        d["atraso_despacho_dias"], errors="coerce"
    )
    d["order_purchase_timestamp"] = pd.to_datetime(
        d["order_purchase_timestamp"], errors="coerce"
    )
    return d


def conclusion(page, data, metrics, comparison, monitored):
    st.subheader("Conclusão de negócio")
    if page in ORIGINAL_CONCLUSIONS:
        st.caption("Conclusão da análise original, calculada sobre a base completa.")
        st.info(ORIGINAL_CONCLUSIONS[page])
    st.caption("Síntese para o recorte selecionado nos filtros.")
    st.write(business_summary(page, data, metrics, comparison, monitored))


def show_chart(chart):
    st.altair_chart(chart, width="stretch")


def remember_filter(key):
    st.session_state[key] = st.session_state["_" + key]


def load_filter(key, default):
    st.session_state.setdefault(key, default)
    st.session_state["_" + key] = st.session_state[key]


def render_filters(data):
    valid_dates = data["order_purchase_timestamp"].dropna()
    if valid_dates.empty:
        raise ValueError("O CSV final não contém datas de compra válidas.")

    states = sorted(data["seller_state"].dropna().unique())
    categories = sorted(
        data["categorias"].dropna().str.split("|", regex=False).explode().unique()
    )
    sellers = sorted(data["seller_id"].dropna().unique())
    first_day, last_day = valid_dates.min().date(), valid_dates.max().date()

    st.subheader("Filtros")
    filter_columns = st.columns(4)
    with filter_columns[0]:
        load_filter("state_filter", ALL_STATES)
        selected_state = st.selectbox(
            "Estado do vendedor",
            [ALL_STATES, *states],
            key="_state_filter",
            on_change=remember_filter,
            args=["state_filter"],
        )
        selected_states = (
            [] if selected_state == ALL_STATES else [selected_state]
        )
    with filter_columns[1]:
        load_filter("category_filter", ALL_CATEGORIES)
        selected_category = st.selectbox(
            "Categoria do produto",
            [ALL_CATEGORIES, *categories],
            key="_category_filter",
            on_change=remember_filter,
            args=["category_filter"],
        )
        selected_categories = (
            [] if selected_category == ALL_CATEGORIES else [selected_category]
        )
    with filter_columns[2]:
        load_filter("sellers", [])
        selected_sellers = st.multiselect(
            "Vendedor",
            sellers,
            key="_sellers",
            placeholder="Todos os vendedores",
            on_change=remember_filter,
            args=["sellers"],
        )
    with filter_columns[3]:
        load_filter("period", (first_day, last_day))
        selected_period = st.date_input(
            "Período da compra",
            min_value=first_day,
            max_value=last_day,
            key="_period",
            format="DD/MM/YYYY",
            on_change=remember_filter,
            args=["period"],
        )

    if (
        not isinstance(selected_period, (tuple, list))
        or len(selected_period) != 2
    ):
        return (
            data.iloc[0:0].copy(),
            selected_states,
            selected_categories,
            selected_sellers,
            None,
            None,
        )
    start, end = selected_period
    filtered = filter_data(
        data,
        selected_states,
        selected_categories,
        selected_sellers,
        start,
        end,
    )
    return (
        filtered,
        selected_states,
        selected_categories,
        selected_sellers,
        start,
        end,
    )


def friendly_metrics(metrics):
    shown = metrics.copy()
    shown["vendedor"] = shown.apply(seller_label, axis=1)
    for column in ("taxa_atraso_despacho_pct", "taxa_nota_baixa_pct"):
        shown[column] = shown[column].round(2)
    shown["nota_media"] = shown["nota_media"].round(2)
    shown["atraso_medio_despacho_dias"] = shown[
        "atraso_medio_despacho_dias"
    ].round(2)
    return shown.rename(
        columns={
            "vendedor": "Vendedor (município e ID)",
            "seller_id": "ID do vendedor",
            "seller_state": "Estado",
            "qtd_pedidos": "Pedidos",
            "pedidos_despacho_avaliavel": "Despachos avaliáveis",
            "pedidos_com_atraso_despacho": "Despachos atrasados",
            "taxa_atraso_despacho_pct": "Atrasos (%)",
            "atraso_medio_despacho_dias": "Atraso médio (dias)",
            "pedidos_com_nota": "Pedidos com nota",
            "nota_media": "Nota média",
            "pedidos_nota_baixa": "Pedidos com nota baixa",
            "taxa_nota_baixa_pct": "Notas baixas (%)",
            "classificacao": "Resultado dos critérios",
        }
    )


def render(page):
    st.set_page_config(page_title="Parceiros | Olist · Grupo 04", layout="wide")
    st.sidebar.title("Parceiros Olist")
    for path, label in (
        ("app.py", "Visão geral"),
        ("pages/1_Atrasos_no_Despacho.py", "Atrasos no despacho"),
        ("pages/2_Atrasos_e_Avaliacoes.py", "Atrasos e avaliações"),
        ("pages/3_Criterios_para_Vendedores.py", "Critérios de acompanhamento"),
    ):
        st.sidebar.page_link(path, label=label)
    st.caption("UNIFSA · CIÊNCIA DE DADOS · GRUPO 04")
    titles = {
        "inicio": "Gestão de vendedores parceiros",
        "atrasos": "Quais vendedores mais atrasam o despacho dos pedidos?",
        "avaliacoes": "Vendedores que atrasam recebem avaliações piores?",
        "criterios": "Que critérios objetivos usar para acompanhar ou advertir vendedores?",
    }
    st.title(titles[page])
    st.write(
        "Compare os indicadores de atraso e avaliação definidos na etapa 6, "
        "usando os filtros para explorar diferentes recortes."
    )
    if not FINAL_CSV.is_file():
        st.error(
            "O CSV final do projeto não foi encontrado em "
            "`tabelas_analiticas/tabela_vendedor_pedido.csv`."
        )
        st.stop()
    original = read_final(str(FINAL_CSV), FINAL_CSV.stat().st_mtime_ns)
    (
        data,
        selected_states,
        selected_categories,
        selected_sellers,
        start,
        end,
    ) = render_filters(original)
    st.caption(
        "Fonte: CSV final do pipeline. Cada linha representa um vendedor em um "
        "pedido; as avaliações pertencem ao pedido e podem aparecer para cada "
        "vendedor participante."
    )
    if start is None or end is None:
        st.info("Selecione as datas inicial e final para aplicar o período.")
    else:
        st.caption(
            f"Período: {start:%d/%m/%Y} a {end:%d/%m/%Y} · "
            f"{len(selected_states) if selected_states != [ALL_STATES] else 'todos'} estados · "
            f"{len(selected_categories) if selected_categories else 'todas'} categorias · "
            f"{len(selected_sellers) if selected_sellers else 'todos'} vendedores."
        )

    metrics = seller_metrics(data)
    comparison = review_comparison(data)
    monitored = monitoring_metrics(data)
    cols = st.columns(4)
    order_count = data["order_id"].nunique()
    dispatch_count = int(data["despacho_avaliavel"].fillna(False).sum())
    review_count = int(data["nota_media_pedido"].notna().sum())
    cols[0].metric("Pedidos no recorte", f"{order_count:,}".replace(",", "."))
    cols[1].metric("Vendedores", f"{metrics['seller_id'].nunique():,}".replace(",", "."))
    cols[2].metric("Despachos avaliáveis", f"{dispatch_count:,}".replace(",", "."))
    cols[3].metric("Pedidos com nota", f"{review_count:,}".replace(",", "."))

    if data.empty:
        st.info(
            "Nenhum pedido corresponde aos filtros atuais. Amplie o período "
            "ou selecione outros estados, categorias ou vendedores."
        )
    elif page == "inicio":
        st.subheader("As três perguntas do briefing")
        st.page_link("pages/1_Atrasos_no_Despacho.py", label="1. Atrasos no despacho")
        st.page_link("pages/2_Atrasos_e_Avaliacoes.py", label="2. Atrasos e avaliações")
        st.page_link(
            "pages/3_Criterios_para_Vendedores.py",
            label="3. Critérios de acompanhamento",
        )
        st.write(
            "O ranking usa a taxa de atraso por vendedor; a comparação de notas "
            "considera pedidos com situação de despacho conhecida; e os "
            "critérios de acompanhamento combinam atraso e avaliações baixas."
        )
        st.caption(
            f"CSV final: {order_count:,} pedidos no recorte. A classificação "
            "é descritiva e não substitui a análise dos registros."
        )
    elif page == "atrasos":
        ranked = delay_ranking(metrics)
        st.subheader("Ranking por taxa de atraso")
        st.caption(
            f"Entram no ranking vendedores com pelo menos {MIN_DISPATCH_ORDERS} "
            "despachos avaliáveis. A taxa é atrasos ÷ despachos avaliáveis."
        )
        if ranked.empty:
            st.info("Nenhum vendedor atingiu o volume mínimo neste recorte.")
        else:
            show_chart(ranking_chart(ranked))
            st.dataframe(friendly_metrics(ranked.head(20)), hide_index=True)
            st.download_button(
                "Baixar o ranking completo",
                friendly_metrics(ranked).to_csv(index=False).encode("utf-8"),
                "ranking_atrasos.csv",
                "text/csv",
            )
    elif page == "avaliacoes":
        st.subheader("Nota média e avaliações baixas por situação do despacho")
        if comparison["nota_media"].notna().any():
            show_chart(review_chart(comparison))
            displayed = comparison.copy()
            displayed["nota_media"] = displayed["nota_media"].round(2)
            displayed["taxa_nota_baixa_pct"] = displayed[
                "taxa_nota_baixa_pct"
            ].round(2)
            st.dataframe(
                displayed.rename(
                    columns={
                        "situacao": "Situação do despacho",
                        "qtd_pedidos": "Pedidos avaliados",
                        "nota_media": "Nota média",
                        "taxa_nota_baixa_pct": "Notas 1 ou 2 (%)",
                    }
                ),
                hide_index=True,
            )
        else:
            st.info(
                "Não há pedidos avaliados com situação de despacho conhecida "
                "neste recorte."
            )
        st.caption(
            "Uma avaliação é considerada baixa quando a nota média do "
            "vendedor-pedido é 1 ou 2. A comparação é descritiva; associação "
            "não comprova causa."
        )
    elif page == "criterios":
        st.subheader("Critérios propostos na etapa 6")
        st.write(
            f"São avaliados vendedores com pelo menos {MIN_DISPATCH_ORDERS} "
            f"despachos avaliáveis e {MIN_REVIEW_ORDERS} pedidos com nota. "
            "A taxa de atraso e a taxa de notas baixas são comparadas ao "
            "limite de 20%."
        )
        if monitored.empty:
            st.info("Nenhum vendedor atingiu os dois volumes mínimos neste recorte.")
        else:
            counts = monitored["classificacao"].value_counts()
            cols = st.columns(3)
            cols[0].metric(
                "Acompanhamento regular",
                f"{counts.get('Acompanhamento regular', 0):,}".replace(",", "."),
            )
            cols[1].metric(
                "Advertência para revisão",
                f"{counts.get('Advertência', 0):,}".replace(",", "."),
            )
            cols[2].metric(
                "Revisão prioritária",
                f"{counts.get('Revisão prioritária', 0):,}".replace(",", "."),
            )
            show_chart(criteria_chart(monitored))
            st.dataframe(friendly_metrics(monitored), hide_index=True)

    if page in ORIGINAL_CONCLUSIONS:
        conclusion(page, data, metrics, comparison, monitored)
    else:
        st.subheader("Síntese do recorte")
        st.write(business_summary(page, data, metrics, comparison, monitored))

    st.download_button(
        "Baixar o recorte analítico (CSV)",
        data.to_csv(index=False).encode("utf-8"),
        "recorte_analitico_vendedor_pedido.csv",
        "text/csv",
    )
    st.caption("Fonte: tabela analítica final do projeto · Olist.")
