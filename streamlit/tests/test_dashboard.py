# [IA] registro 13 - testes do recorte PI e dos gráficos interativos.
from datetime import date
from pathlib import Path
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['app.py', 'pages/1_Atrasos_no_Despacho.py',
    'pages/2_Atrasos_e_Avaliacoes.py', 'pages/3_Criterios_para_Vendedores.py']


@pytest.fixture(scope='module')
def pi():
    d = pd.read_csv(ROOT / 'data/processed/tabela_analitica.csv', parse_dates=['order_purchase_timestamp'])
    return d[d.seller_state.eq('PI')].copy()


def open_page(page='app.py'):
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=40).run()
    if page != 'app.py':
        at.switch_page(page).run()
    return at


@pytest.mark.parametrize('page', PAGES)
def test_pages_use_only_pi_and_have_business_conclusion(page, pi):
    at = open_page(page)
    assert not at.exception
    assert int(at.metric[0].value.replace('.', '')) == pi.order_id.nunique()
    assert int(at.metric[1].value.replace('.', '')) == pi.eligible_dispatch.sum()
    assert int(at.metric[3].value.replace('.', '')) == pi.eligible_review.sum()
    assert at.selectbox[1].options == ['PI']
    assert at.selectbox[1].disabled
    assert 'Conclusão de negócio' in [element.value for element in at.subheader]
    assert 'Loja Aurora' in at.multiselect[0].options
    assert at.get('arrow_vega_lite_chart')


@pytest.mark.parametrize('page', PAGES)
def test_all_months_update_analysis_pages(page, pi):
    import pyarrow as pa
    at = open_page(page)
    at.selectbox[0].set_value('2018').run()
    for number, name in enumerate(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'], 1):
        at.selectbox[2].set_value(name).run()
        assert not at.exception
        expected = pi[pi.order_purchase_timestamp.dt.month.eq(number)]
        if expected.empty:
            assert at.metric[0].value == '0'
            assert at.metric[1].value == '0'
            assert at.metric[2].value == 'Sem dados'
            assert at.dataframe[0].value.empty
            assert any('Nenhum pedido' in element.value for element in at.info)
            continue
        assert int(at.metric[0].value) == expected.order_id.nunique()
        assert int(at.metric[1].value) == expected.eligible_dispatch.sum()
        assert int(at.metric[3].value) == expected.eligible_review.sum()
        assert at.date_input[0].value[0].month == number
        assert at.date_input[0].value[1].month == number
        assert at.get('arrow_vega_lite_chart')
        assert at.dataframe
        window = expected
        if page == PAGES[3]:
            end = expected.order_purchase_timestamp.max().normalize()
            window = expected[expected.order_purchase_timestamp.ge(end - pd.Timedelta(days=29))]
        eligible = window[window.eligible_dispatch]
        reviewed = window[window.eligible_review]
        for chart in at.get('arrow_vega_lite_chart'):
            for dataset in chart.proto.datasets:
                values = pa.ipc.open_stream(dataset.data.data).read_all().to_pandas()
                if 'eligible_orders' in values:
                    assert values.eligible_orders.sum() == len(eligible)
                if 'review_count' in values:
                    assert values.review_count.sum() == len(reviewed)
                if 'mean_score' in values:
                    assert values.mean_score.mean() == pytest.approx(reviewed.review_score.mean())
                if 'purchase_month' in values:
                    assert set(values.purchase_month) == {f'2018-{number:02}'}
                    assert values['count'].sum() == len(eligible)
        table = at.dataframe[0].value
        if page in PAGES[:2]:
            count_column = 'Pedidos elegíveis'
        elif page == PAGES[2]:
            count_column = 'Pedidos avaliados'
        else:
            count_column = 'Pedidos elegíveis'
        assert table[count_column].sum() == (len(reviewed) if page == PAGES[2] else len(eligible))
    at.selectbox[2].set_value('Todos os meses').run()
    assert int(at.metric[0].value) == pi.order_id.nunique()


@pytest.mark.parametrize('page', PAGES)
def test_year_selection_restores_whole_year_and_twelve_months(page, pi):
    at = open_page(page)
    assert len(at.selectbox[2].options) == 13
    assert at.selectbox[2].options[-1] == 'Dezembro'
    at.selectbox[2].set_value('Fevereiro').run()
    assert at.metric[0].value == '5'
    at.selectbox[0].set_value('2018').run()
    assert not at.exception
    assert at.selectbox[2].value == 'Todos os meses'
    assert at.date_input[0].value == (date(2018, 1, 1), date(2018, 12, 31))
    assert int(at.metric[0].value) == pi.order_id.nunique()
    at.selectbox[2].set_value('Dezembro').run()
    assert not at.exception
    assert at.metric[0].value == '0'
    at.selectbox[0].set_value('Todos os anos').run()
    assert not at.exception
    assert at.selectbox[2].value == 'Todos os meses'
    assert int(at.metric[0].value) == pi.order_id.nunique()


def test_month_updates_period_and_results_without_manual_dates(pi):
    at = open_page()
    at.date_input[0].set_value((date(2018, 1, 5), date(2018, 1, 31))).run()
    at.selectbox[2].set_value('Fevereiro').run()
    assert not at.exception
    assert at.date_input[0].value == (date(2018, 2, 1), date(2018, 2, 28))
    expected = pi[pi.order_purchase_timestamp.dt.month.eq(2)]
    assert int(at.metric[0].value) == expected.order_id.nunique()
    assert at.get('arrow_vega_lite_chart')
    at.selectbox[2].set_value('Junho').run()
    assert not at.exception
    assert at.date_input[0].value == (date(2018, 6, 1), date(2018, 6, 30))
    assert any('Nenhum pedido' in element.value for element in at.info)
    at.selectbox[2].set_value('Todos os meses').run()
    assert not at.exception
    assert int(at.metric[0].value) == pi.order_id.nunique()


def test_charts_have_tooltips_and_zoom_and_aliases_preserve_ids(pi):
    import json
    from src.analysis import seller_metrics, review_comparison
    from src.presentation import named_metrics
    from src.visualizations import ranking_chart, review_chart, monthly_chart, seller_scatter
    metrics = seller_metrics(pi)
    shown = named_metrics(metrics)
    assert shown.seller_id.tolist() == metrics.seller_id.tolist()
    assert shown.seller_name.tolist() == ['Loja Aurora']
    monthly = pi[pi.eligible_dispatch].groupby('purchase_month').dispatch_late.agg(['mean', 'count'])
    charts = [ranking_chart(metrics), review_chart(review_comparison(pi)), monthly_chart(monthly), seller_scatter(metrics)]
    for chart in charts:
        spec = chart.to_dict()
        assert 'tooltip' in json.dumps(spec)
        assert any(parameter.get('bind') == 'scales' for parameter in spec['params'])


def test_filters_are_preserved_between_pages(pi):
    at = open_page()
    seller = pi.seller_id.iloc[0]
    at.selectbox[0].set_value('2018').run()
    at.selectbox[2].set_value('Fevereiro').run()
    at.multiselect[0].set_value([seller]).run()
    expected = pi[pi.order_purchase_timestamp.dt.month.eq(2)]
    assert not at.exception
    assert int(at.metric[0].value.replace('.', '')) == expected.order_id.nunique()
    at.switch_page('pages/2_Atrasos_e_Avaliacoes.py').run()
    assert not at.exception
    assert at.selectbox[0].value == '2018'
    assert at.selectbox[2].value == 'Fevereiro'
    assert at.multiselect[0].value == [seller]
    assert int(at.metric[0].value.replace('.', '')) == expected.order_id.nunique()


def test_incomplete_period_and_empty_period():
    at = open_page()
    at.date_input[0].set_value((date(2018, 6, 1),)).run()
    assert not at.exception
    assert at.info
    at.date_input[0].set_value((date(2018, 6, 1), date(2018, 6, 30))).run()
    assert not at.exception
    assert at.metric[0].value == '0'
    assert any('Nenhum pedido' in element.value for element in at.info)


@pytest.mark.parametrize('page', PAGES)
def test_only_ineligible_order_has_explanation_instead_of_blank_chart(page):
    at = open_page(page)
    at.date_input[0].set_value((date(2018, 1, 5), date(2018, 1, 5))).run()
    assert not at.exception
    assert at.metric[0].value == '1'
    assert at.metric[1].value == '0'
    assert at.metric[2].value == 'Sem dados'
    assert at.info
    assert not at.get('arrow_vega_lite_chart')


def test_small_pi_sample_does_not_claim_late_review_comparison():
    at = open_page('pages/2_Atrasos_e_Avaliacoes.py')
    assert not at.exception
    texts = [element.value for element in at.markdown]
    assert any('não é possível comparar' in text.lower() for text in texts)
    assert any('4,00' in text and '11' in text for text in texts)


def test_scenario_controls_do_not_change_general_indicators():
    at = open_page('pages/3_Criterios_para_Vendedores.py')
    original = [metric.value for metric in at.metric]
    at.number_input[0].set_value(1).run()
    at.slider[0].set_value(0).run()
    assert not at.exception
    assert [metric.value for metric in at.metric] == original
    assert not at.dataframe[-1].value['Resultado do cenário'].eq('Acima do limiar informado').any()
