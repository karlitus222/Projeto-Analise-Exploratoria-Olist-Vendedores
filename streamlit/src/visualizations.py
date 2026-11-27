"""Gráficos interativos do painel; os cálculos ficam em analysis.py."""
# [IA] registro 13
import altair as alt
from .presentation import named_metrics


def ranking_chart(metrics):
    data = named_metrics(metrics.head(12))
    data['late_percent'] = data.late_rate * 100
    selection = alt.selection_point(fields=['seller_id'], name='vendedor_destacado')
    base = alt.Chart(data).encode(
        x=alt.X('late_percent:Q', title='Despachos atrasados (%)', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('seller_name:N', title='Vendedor (nome fictício)', sort='-x'),
        tooltip=[alt.Tooltip('seller_name:N', title='Vendedor'), alt.Tooltip('seller_id:N', title='ID original'),
            alt.Tooltip('eligible_orders:Q', title='Pedidos elegíveis'), alt.Tooltip('late_orders:Q', title='Atrasos'),
            alt.Tooltip('late_percent:Q', title='Taxa de atraso (%)', format='.2f')],
        opacity=alt.condition(selection, alt.value(1), alt.value(.3)))
    return (base.mark_bar(color='#087F8C') + base.mark_point(color='#087F8C', filled=True, size=110)).add_params(
        selection).properties(height=170).interactive(bind_y=False)


def review_chart(comparison):
    data = comparison.copy()
    data['dispatch_group'] = data.dispatch_late.map({0: 'Em prazo', 1: 'Com atraso'})
    selection = alt.selection_point(fields=['dispatch_group'], name='grupo_destacado')
    return alt.Chart(data).mark_bar(size=70).encode(
        x=alt.X('dispatch_group:N', title='Despacho'),
        y=alt.Y('mean_score:Q', title='Nota média', scale=alt.Scale(domain=[0, 5])),
        color=alt.Color('dispatch_group:N', title='Despacho', scale=alt.Scale(
            domain=['Em prazo', 'Com atraso'], range=['#087F8C', '#E58F37'])),
        opacity=alt.condition(selection, alt.value(1), alt.value(.3)),
        tooltip=[alt.Tooltip('dispatch_group:N', title='Despacho'),
            alt.Tooltip('review_count:Q', title='Pedidos avaliados'),
            alt.Tooltip('mean_score:Q', title='Nota média', format='.2f')]
    ).add_params(selection).properties(height=280).interactive(bind_x=False)


def monthly_chart(monthly):
    data = monthly.reset_index().copy()
    data['late_percent'] = data['mean'] * 100
    return alt.Chart(data).mark_line(point=True, color='#087F8C').encode(
        x=alt.X('purchase_month:O', title='Mês da compra'),
        y=alt.Y('late_percent:Q', title='Atrasos (%)', scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip('purchase_month:O', title='Mês'),
            alt.Tooltip('count:Q', title='Pedidos elegíveis'),
            alt.Tooltip('late_percent:Q', title='Atrasos (%)', format='.2f')]
    ).properties(height=270).interactive(bind_x=False)


def seller_scatter(metrics):
    data = named_metrics(metrics.dropna(subset=['mean_score', 'late_rate']))
    data['late_percent'] = data.late_rate * 100
    selection = alt.selection_point(fields=['seller_id'], name='parceiro_destacado')
    return alt.Chart(data).mark_circle(size=180).encode(
        x=alt.X('late_percent:Q', title='Atrasos (%)', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('mean_score:Q', title='Nota média', scale=alt.Scale(domain=[0, 5])),
        color=alt.value('#087F8C'),
        opacity=alt.condition(selection, alt.value(1), alt.value(.3)),
        tooltip=[alt.Tooltip('seller_name:N', title='Vendedor'), alt.Tooltip('seller_id:N', title='ID original'),
            alt.Tooltip('review_count:Q', title='Pedidos avaliados'),
            alt.Tooltip('late_percent:Q', title='Atrasos (%)', format='.2f'),
            alt.Tooltip('mean_score:Q', title='Nota média', format='.2f')]
    ).add_params(selection).properties(height=270).interactive()
