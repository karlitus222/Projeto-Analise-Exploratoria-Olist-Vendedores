# [IA] registro 22
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.analysis import delay_ranking, filter_data, monitoring_metrics, review_comparison, seller_metrics
from src.dashboard import FINAL_CSV
from src.visualizations import ranking_chart


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "pages/1_Atrasos_no_Despacho.py",
    "pages/2_Atrasos_e_Avaliacoes.py",
    "pages/3_Criterios_para_Vendedores.py",
]


def seller_rows(seller_id, state, dispatch_flags, ratings, category="livros"):
    rows = []
    total = max(len(dispatch_flags), len(ratings))
    for index in range(total):
        dispatch_flag = dispatch_flags[index] if index < len(dispatch_flags) else None
        rating = ratings[index] if index < len(ratings) else None
        rows.append(
            {
                "seller_id": seller_id,
                "order_id": f"{seller_id}-{index}",
                "seller_state": state,
                "seller_city": f"cidade-{seller_id}",
                "categorias": category,
                "order_purchase_timestamp": date(2018, 1, 1)
                + timedelta(days=index),
                "despacho_avaliavel": dispatch_flag is not None,
                "flag_atraso_despacho": dispatch_flag,
                "atraso_despacho_dias": (
                    1 if dispatch_flag is True else 0 if dispatch_flag is False else None
                ),
                "nota_media_pedido": rating,
            }
        )
    return rows


@pytest.fixture
def indicator_data():
    rows = []
    rows += seller_rows(
        "prioritario",
        "SP",
        [True] * 5 + [False] * 15,
        [2, 2] + [4] * 8,
        "livros",
    )
    rows += seller_rows(
        "alerta-atraso",
        "RJ",
        [True] * 4 + [False] * 16,
        [4] * 10,
        "brinquedos",
    )
    rows += seller_rows(
        "alerta-nota",
        "MG",
        [False] * 20,
        [2, 2] + [4] * 8,
        "livros",
    )
    rows += seller_rows("regular", "BA", [False] * 20, [4] * 10)
    rows += seller_rows("volume-baixo", "SP", [True] * 19, [2] * 10)
    return pd.DataFrame(rows)


def test_ranking_uses_the_same_twenty_order_cutoff_and_delay_rate(indicator_data):
    metrics = seller_metrics(indicator_data)
    ranking = delay_ranking(metrics)

    assert "volume-baixo" not in set(ranking.seller_id)
    top = ranking.set_index("seller_id").loc["prioritario"]
    assert top.pedidos_com_atraso_despacho == 5
    assert top.pedidos_despacho_avaliavel == 20
    assert top.taxa_atraso_despacho_pct == 25


def test_ranking_chart_uses_display_seller_labels(indicator_data):
    metrics = seller_metrics(indicator_data)
    chart_spec = ranking_chart(delay_ranking(metrics).head(1)).to_dict()

    assert "Cidade-Prioritario, SP · priorit" in str(chart_spec)
    assert "undefined" not in str(chart_spec)


def test_review_comparison_uses_rated_orders_with_known_dispatch():
    rows = seller_rows("late", "SP", [True, True], [1, 3])
    rows += seller_rows("on-time", "RJ", [False, False], [4, 5])
    comparison = review_comparison(pd.DataFrame(rows))
    groups = comparison.set_index("situacao")

    assert groups.loc["Com atraso no despacho", "nota_media"] == pytest.approx(2.0)
    assert groups.loc["Com atraso no despacho", "taxa_nota_baixa_pct"] == pytest.approx(50)
    assert groups.loc["Sem atraso no despacho", "nota_media"] == pytest.approx(4.5)
    assert groups.loc["Sem atraso no despacho", "taxa_nota_baixa_pct"] == pytest.approx(0)


def test_monitoring_uses_original_sample_and_threshold_rules(indicator_data):
    monitored = monitoring_metrics(indicator_data).set_index("seller_id")

    assert set(monitored.index) == {
        "prioritario",
        "alerta-atraso",
        "alerta-nota",
        "regular",
    }
    assert monitored.loc["prioritario", "classificacao"] == "Revisão prioritária"
    assert monitored.loc["alerta-atraso", "classificacao"] == "Advertência"
    assert monitored.loc["alerta-nota", "classificacao"] == "Advertência"
    assert monitored.loc["regular", "classificacao"] == "Acompanhamento regular"


def test_filters_apply_state_category_and_inclusive_dates(indicator_data):
    filtered = filter_data(
        indicator_data,
        ["SP"],
        ["livros"],
        [],
        date(2018, 1, 2),
        date(2018, 1, 4),
    )

    assert set(filtered.seller_id) == {"prioritario"}
    assert len(filtered) == 3
    assert filtered.order_purchase_timestamp.min() == date(2018, 1, 2)
    assert filtered.order_purchase_timestamp.max() == date(2018, 1, 4)


def test_empty_state_selection_includes_all_states(indicator_data):
    filtered = filter_data(indicator_data, [], [], [], None, None)

    assert len(filtered) == len(indicator_data)


def open_page(page):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    if page != "app.py":
        app.switch_page(page).run()
    return app


@pytest.mark.parametrize("page", PAGES)
def test_briefing_pages_load_final_csv_show_filters_and_original_conclusion(page):
    assert FINAL_CSV.is_file()
    app = open_page(page)

    assert not app.exception
    assert "Conclusão de negócio" in [element.value for element in app.subheader]
    assert len(app.multiselect) >= 1
    labels = [element.label for element in app.multiselect]
    assert "Vendedor" in labels
    assert "Vendedor (opcional)" not in labels
    selectboxes = {element.label: element for element in app.selectbox}
    assert "Estado do vendedor" in selectboxes
    assert "Categoria do produto" in selectboxes
    state_filter = selectboxes["Estado do vendedor"]
    category_filter = selectboxes["Categoria do produto"]
    assert state_filter.value == "Todos os estados"
    assert category_filter.value == "Todas as categorias"
    assert any("Conclusão" in element.value for element in app.info)
    assert app.get("arrow_vega_lite_chart")
