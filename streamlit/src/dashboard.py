"""Interface gerencial; a única fonte numérica é o CSV analítico final."""
# [IA] registro 2
import pandas as pd
import streamlit as st
from .load_data import ROOT
from .analysis import filter_data, seller_metrics, review_comparison, monitoring_metrics
from .visualizations import ranking_chart, review_chart, monthly_chart, seller_scatter
from .presentation import seller_name, named_metrics, business_summary


@st.cache_data
def read_final(path, modified_ns):
    d = pd.read_csv(path, dtype={'order_id': 'string', 'seller_id': 'string'})
    for c in ['eligible_dispatch', 'eligible_review', 'invalid_chronology', 'deadlines_complete', 'dispatch_time_outlier']:
        d[c] = d[c].astype('string').str.lower().eq('true')
    d['order_purchase_timestamp'] = pd.to_datetime(d.order_purchase_timestamp, errors='coerce')
    return d


def conclusion(key, data, metrics):
    # [IA] registro 13: a síntese acompanha o PI; respostas nacionais são referência no arquivo original.
    st.subheader('Conclusão de negócio')
    st.caption('Síntese descritiva calculada para os filtros atuais do PI.')
    st.write(business_summary(key, data, metrics))


def show_chart(chart):
    st.altair_chart(chart, width='stretch')


# [IA] registro 13: chaves permanentes evitam perder os filtros ao trocar de página.
def remember_filter(key):
    st.session_state[key] = st.session_state['_' + key]


def load_filter(key, default):
    st.session_state.setdefault(key, default)
    st.session_state['_' + key] = st.session_state[key]


def update_calendar_filter(key, valid_dates, months):
    remember_filter(key)
    if key == 'pi_year':
        st.session_state['pi_month'] = 'Todos os meses'
    year = st.session_state.get('pi_year', 'Todos os anos')
    month = st.session_state.get('pi_month', 'Todos os meses')
    first_year = valid_dates.min().year if year == 'Todos os anos' else int(year)
    last_year = valid_dates.max().year if year == 'Todos os anos' else int(year)
    first, last = pd.Timestamp(first_year, 1, 1), pd.Timestamp(last_year, 12, 31)
    if month != 'Todos os meses':
        first_month = pd.Timestamp(first.year, months[month], 1)
        last_month = pd.Timestamp(last.year, months[month], 1) + pd.offsets.MonthEnd(0)
        first, last = max(first, first_month), min(last, last_month)
    st.session_state['pi_period'] = (first.date(), last.date())


def friendly_metrics(metrics):
    shown = named_metrics(metrics)
    for col in ['late_rate', 'negative_rate', 'late_ci_low', 'late_ci_high']:
        shown[col] = (shown[col] * 100).round(2)
    return shown.round(2).rename(columns={'seller_name': 'Vendedor (nome fictício)', 'seller_id': 'ID original', 'observed_orders': 'Pedidos observados',
        'sales_value': 'Valor dos itens (R$)', 'eligible_orders': 'Pedidos elegíveis', 'late_orders': 'Pedidos atrasados',
        'late_rate': 'Atrasos (%)', 'mean_delay_days': 'Excesso médio (dias)', 'median_dispatch_days': 'Mediana até despacho (dias)',
        'review_count': 'Pedidos com nota', 'mean_score': 'Nota média', 'negative_count': 'Notas 1 ou 2',
        'negative_rate': 'Notas negativas (%)', 'late_ci_low': 'Limite inferior 95% (%)', 'late_ci_high': 'Limite superior 95% (%)',
        'cenario': 'Resultado do cenário', 'mean_business_days': 'Média até despacho (dias úteis)',
        'above_tad_limit': 'TAD acima de 10%', 'below_score_floor': 'Nota abaixo de 3,8'})


def render(page):
    st.set_page_config(page_title='Parceiros | Olist · Grupo 04', layout='wide')
    st.sidebar.title('Parceiros Olist')
    for path, label in [('app.py', 'Visão geral'), ('pages/1_Atrasos_no_Despacho.py', 'Atrasos no despacho'),
            ('pages/2_Atrasos_e_Avaliacoes.py', 'Atrasos e avaliações'), ('pages/3_Criterios_para_Vendedores.py', 'Critérios de acompanhamento')]:
        st.sidebar.page_link(path, label=label)
    st.caption('UNIFSA · CIÊNCIA DE DADOS · GRUPO 04')
    titles = {'inicio': 'Gestão de vendedores parceiros', 'atrasos': 'Quais vendedores mais atrasam o despacho?',
              'avaliacoes': 'Vendedores que atrasam recebem avaliações piores?',
              'criterios': 'Critérios para acompanhar vendedores'}
    st.title(titles[page])
    st.write('Acompanhe prazos e avaliações dos parceiros no período selecionado.')
    path = ROOT / 'data/processed/tabela_analitica.csv'
    if not path.exists():
        st.info('Base analítica não encontrada. Coloque a tabela consolidada do grupo em data/processed/tabela_analitica.csv, conforme o README.')
        st.stop()
    d = read_final(str(path), path.stat().st_mtime_ns)
    d = d[d.seller_state.eq('PI')].copy()
    if d.empty:
        st.info('A tabela não contém pedidos de vendedores do PI.')
        st.stop()
    st.caption('Recorte fixo: Piauí (PI). Nomes fictícios para demonstração; os IDs originais são preservados.')
    # [IA] registro 12: filtros principais no topo, conforme a referência visual.
    valid_dates = d.order_purchase_timestamp.dropna()
    months = {'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
        'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12}
    years = [str(year) for year in sorted(valid_dates.dt.year.unique())]
    year_column, state_column = st.columns(2)
    load_filter('pi_year', 'Todos os anos')
    year = year_column.selectbox('Ano da compra', ['Todos os anos'] + years, key='_pi_year',
        on_change=update_calendar_filter, args=['pi_year', valid_dates, months])
    state_column.selectbox('Estado (UF)', ['PI'], disabled=True)
    start = end = None
    with st.expander('Mais filtros: mês, período e vendedor'):
        st.caption('Ano e mês ajustam o período automaticamente. Você pode refinar os dias depois. '
            'Trocar o ano restaura todos os meses. Os filtros são mantidos ao trocar de página.')
        month_column, seller_column = st.columns(2)
        load_filter('pi_month', 'Todos os meses')
        month = month_column.selectbox('Mês da compra', ['Todos os meses'] + list(months),
            key='_pi_month', on_change=update_calendar_filter, args=['pi_month', valid_dates, months])
        load_filter('pi_sellers', [])
        sellers = seller_column.multiselect('Vendedor', sorted(d.seller_id.dropna().unique()),
            key='_pi_sellers', format_func=seller_name, placeholder='Todos os vendedores',
            on_change=remember_filter, args=['pi_sellers'])
        if not valid_dates.empty:
            first_day = pd.Timestamp(valid_dates.min().year, 1, 1).date()
            last_day = pd.Timestamp(valid_dates.max().year, 12, 31).date()
            load_filter('pi_period', (first_day, last_day))
            dates = st.date_input('Período da compra', min_value=first_day,
                max_value=last_day, key='_pi_period', format='DD/MM/YYYY',
                on_change=remember_filter, args=['pi_period'])
            if len(dates) != 2:
                st.info('Selecione a data inicial e a data final.')
                st.stop()
            start, end = dates
    d = filter_data(d, ['PI'], sellers, start, end)
    if year != 'Todos os anos':
        d = d[d.order_purchase_timestamp.dt.year.eq(int(year))]
    if month != 'Todos os meses':
        d = d[d.order_purchase_timestamp.dt.month.eq(months[month])]
    if start is not None and end is not None:
        st.caption(f'Período aplicado: {start:%d/%m/%Y} a {end:%d/%m/%Y}. Mês: {month}.')
    eligible = d[d.eligible_dispatch]
    reviewed = d[d.eligible_review]
    cols = st.columns(4)
    cols[0].metric('Pedidos no recorte', f'{d.order_id.nunique():,}'.replace(',', '.'))
    cols[1].metric('Despachos elegíveis', f'{len(eligible):,}'.replace(',', '.'))
    rate = eligible.dispatch_late.mean()
    cols[2].metric('Taxa de atraso', f'{rate:.1%}'.replace('.', ',') if pd.notna(rate) else 'Sem dados')
    cols[3].metric('Pedidos com nota', f'{len(reviewed):,}'.replace(',', '.'))
    if d.empty:
        st.info('Nenhum pedido registrado na base do PI para este período e estes filtros. '
            'O total é 0; não há notas ou despachos para calcular médias e taxas.')
        st.dataframe(d[['order_id', 'seller_id', 'order_purchase_timestamp', 'review_score']].rename(
            columns={'order_id': 'Pedido', 'seller_id': 'ID original',
                'order_purchase_timestamp': 'Data da compra', 'review_score': 'Nota'}), hide_index=True)
        conclusion(page, d, pd.DataFrame())
        return
    st.caption('Taxa = pedidos com despacho após o prazo / pedidos elegíveis. Um pedido elegível tem um único vendedor observado, datas coerentes e prazo em todos os itens.')
    st.warning('A data de despacho é do pedido inteiro. Pedidos com vários vendedores ficam fora da comparação individual. Em amostras parciais, um vendedor observado não comprova vendedor único na base completa.')
    metrics = seller_metrics(d)
    st.caption('Gráficos interativos: toque ou passe o cursor para ver detalhes; arraste e use a rolagem para explorar. '
        'Dois cliques restauram a visualização. O zoom não muda os indicadores do recorte.')
    if page == 'inicio':
        st.subheader('Despachos ao longo do período')
        monthly = eligible.groupby('purchase_month').dispatch_late.agg(['mean', 'count'])
        if monthly.empty:
            st.info('Há pedidos neste período, mas nenhum despacho elegível para o gráfico.')
        else:
            show_chart(monthly_chart(monthly))
        st.subheader('Resumo mensal do recorte')
        summary = monthly.rename(columns={'mean': 'Atrasos (%)', 'count': 'Pedidos elegíveis'}).copy()
        summary['Atrasos (%)'] *= 100
        st.dataframe(summary.round(2).rename_axis('Mês da compra'))
        st.caption('Tabela interativa: ordene pelas colunas, pesquise ou baixe os dados pelo menu da tabela.')
        st.subheader('Três perguntas, uma base de evidências')
        st.page_link('pages/1_Atrasos_no_Despacho.py', label='1. Atrasos no despacho')
        st.page_link('pages/2_Atrasos_e_Avaliacoes.py', label='2. Atrasos e avaliações')
        st.page_link('pages/3_Criterios_para_Vendedores.py', label='3. Critérios de acompanhamento')
        st.write('Atraso no despacho compara a entrega à transportadora ao menor prazo dos itens. Atraso ao cliente compara a data de entrega ao dia prometido.')
        st.caption('Base histórica Olist; nenhum modelo de previsão foi utilizado. Dados agregados não demonstram causalidade.')
    elif page == 'atrasos':
        minimum = st.number_input('Mínimo de pedidos elegíveis no gráfico', 1, 10000, 1, key='min_orders')
        ranked = metrics[metrics.eligible_orders.ge(minimum)]
        st.subheader('Frequência e intensidade no recorte')
        if ranked.empty:
            st.info('Nenhum vendedor alcançou o volume mínimo informado.')
        else:
            show_chart(ranking_chart(ranked))
        st.dataframe(friendly_metrics(ranked), hide_index=True)
        st.caption('Excesso médio: max(despacho - prazo, 0) em todos os pedidos elegíveis. Intervalos de Wilson indicam incerteza amostral; o volume mínimo é um filtro exploratório.')
        monthly = eligible.groupby('purchase_month').dispatch_late.agg(['mean', 'count'])
        st.subheader('Evolução mensal')
        if monthly.empty:
            st.info('Há pedidos neste período, mas nenhum despacho elegível para o gráfico.')
        else:
            show_chart(monthly_chart(monthly))
        monthly['mean'] *= 100
        st.dataframe(monthly.round(2).rename(columns={'mean': 'Atrasos (%)', 'count': 'Pedidos elegíveis'}).rename_axis('Mês da compra'))
    elif page == 'avaliacoes':
        comparison = review_comparison(d)
        if comparison.empty:
            st.info('Não há avaliações elegíveis neste período para o gráfico.')
        else:
            show_chart(review_chart(comparison))
        displayed = comparison.copy()
        displayed['dispatch_late'] = displayed.dispatch_late.map({0: 'Em prazo', 1: 'Com atraso'})
        displayed['negative_rate'] *= 100
        st.dataframe(displayed.rename(columns={'dispatch_late': 'Despacho', 'review_count': 'Pedidos avaliados',
            'mean_score': 'Nota média', 'negative_rate': 'Notas 1 ou 2 (%)'}), hide_index=True)
        st.caption('Uma avaliação por pedido: última resposta registrada, com desempate determinístico. Notas 1 e 2 são negativas. Ausências ficam fora do denominador.')
        st.subheader('Comparação entre vendedores')
        if not metrics.dropna(subset=['mean_score', 'late_rate']).empty:
            show_chart(seller_scatter(metrics))
            if len(metrics) < 2:
                st.caption('Há somente um vendedor neste recorte; o ponto não permite comparar parceiros.')
        st.subheader('Controle descritivo por atraso ao cliente')
        strata = reviewed.groupby(['dispatch_late', 'delivery_late'], dropna=False).agg(
            pedidos=('order_id', 'size'), nota_media=('review_score', 'mean')).reset_index()
        for c in ['dispatch_late', 'delivery_late']:
            strata[c] = strata[c].map({0: 'Em prazo', 1: 'Com atraso'}).fillna('Sem informação')
        st.dataframe(strata.rename(columns={'dispatch_late': 'Despacho', 'delivery_late': 'Entrega ao cliente',
            'pedidos': 'Pedidos avaliados', 'nota_media': 'Nota média'}).round(2), hide_index=True)
        st.caption('Associação não implica causalidade. Transporte, categoria, período e perfil do pedido podem afetar as notas. O recorte por atraso ao cliente é descritivo.')
    elif page == 'criterios':
        # [IA] registro 5: definições e limites aprovados pelo solicitante.
        st.subheader('Critérios propostos pela equipe')
        recent, first_day, last_day = monitoring_metrics(d)
        if first_day is not None:
            st.caption(f'Compras de {first_day:%d/%m/%Y} a {last_day:%d/%m/%Y}: últimos 30 dias até a última compra do recorte filtrado, não até a data atual.')
        if not recent.empty:
            st.subheader('Nota média e atraso na janela de acompanhamento')
            if recent.dropna(subset=['mean_score', 'late_rate']).empty:
                st.info('Não há vendedores com despacho e avaliação elegíveis nesta janela para o gráfico.')
            else:
                show_chart(seller_scatter(recent))
            st.caption('Cada ponto representa um vendedor na janela indicada. '
                'No recorte PI há somente um vendedor; passe o cursor ou toque no ponto para ver os valores.')
            st.dataframe(friendly_metrics(recent), hide_index=True)
        st.caption('TAD > 10%; nota média < 3,8. Cada pedido elegível com nota tem peso 1: soma das notas / quantidade de notas. Dias úteis: segunda a sexta no intervalo da aprovação até o despacho, sem feriados. O tempo médio é acompanhado sem limite automático, pois a equipe não definiu esse limite. Volumes e ausências devem ser considerados antes de qualquer advertência.')
        st.subheader('Simulador de critérios para discussão da equipe')
        st.write('Teste outros volumes e limiares abaixo. O cenário não altera os critérios de acompanhamento apresentados acima.')
        minimum = st.number_input('Volume mínimo de pedidos elegíveis', 1, 10000, 30)
        threshold = st.slider('Limiar de atraso do cenário (%)', 0, 100, 10)
        metrics['cenario'] = 'Abaixo do volume informado'
        volume = metrics.eligible_orders.ge(minimum)
        metrics.loc[volume, 'cenario'] = 'Dentro do limiar informado'
        metrics.loc[volume & metrics.late_rate.gt(threshold / 100), 'cenario'] = 'Acima do limiar informado'
        st.dataframe(friendly_metrics(metrics), hide_index=True)
        st.caption('A classificação não é recomendação de advertência. Validar os registros, observar recorrência mensal, comparar mix e ouvir o vendedor antes de decidir.')
    conclusion(page, d, metrics)
    st.download_button('Baixar o recorte analítico (CSV)', d.to_csv(index=False).encode('utf-8'), 'recorte_analitico.csv', 'text/csv')
    st.caption('Fonte: Olist / Kaggle. Assistência de IA registrada em uso_de_ia.md.')
