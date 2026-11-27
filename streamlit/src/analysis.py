"""Métricas recalculadas sobre o recorte da tabela final."""
# [IA] registro 2
import numpy as np
import pandas as pd


def filter_data(d, states, sellers, start, end):
    mask = pd.Series(True, index=d.index)
    if states:
        mask &= d.seller_state.isin(states)
    if sellers:
        mask &= d.seller_id.isin(sellers)
    dates = pd.to_datetime(d.order_purchase_timestamp, errors='coerce')
    if start is not None:
        mask &= dates.ge(pd.Timestamp(start))
    if end is not None:
        mask &= dates.lt(pd.Timestamp(end) + pd.Timedelta(days=1))
    return d.loc[mask].copy()


def seller_metrics(d):
    base = d.groupby('seller_id').agg(observed_orders=('order_id', 'nunique'),
        sales_value=('sales_value', lambda x: x.sum(min_count=1)))
    e = d.loc[d.eligible_dispatch.astype(bool)].copy()
    e['positive_delay'] = e.dispatch_delay_days.clip(lower=0)
    dispatch = e.groupby('seller_id').agg(eligible_orders=('order_id', 'size'), late_orders=('dispatch_late', 'sum'),
        mean_delay_days=('positive_delay', 'mean'), median_dispatch_days=('approval_to_carrier_days', 'median'))
    r = d.loc[d.eligible_review.astype(bool)]
    reviews = r.groupby('seller_id').agg(review_count=('review_score', 'count'), mean_score=('review_score', 'mean'),
        negative_count=('negative_review', 'sum'))
    out = base.join(dispatch).join(reviews).reset_index()
    for c in ['eligible_orders', 'late_orders', 'review_count', 'negative_count']:
        out[c] = out[c].fillna(0).astype(int)
    out['late_rate'] = out.late_orders.div(out.eligible_orders.replace(0, np.nan))
    out['negative_rate'] = out.negative_count.div(out.review_count.replace(0, np.nan))
    # Intervalo de Wilson 95%, descritivo; não corrige confusão nem dependência temporal.
    n = out.eligible_orders.replace(0, np.nan)
    p = out.late_rate
    center = (p + 1.96**2 / (2*n)) / (1 + 1.96**2/n)
    margin = 1.96 * np.sqrt(p*(1-p)/n + 1.96**2/(4*n*n)) / (1 + 1.96**2/n)
    out['late_ci_low'], out['late_ci_high'] = center - margin, center + margin
    return out.sort_values(['late_rate', 'eligible_orders', 'seller_id'], ascending=[False, False, True], na_position='last')


def review_comparison(d):
    r = d.loc[d.eligible_review.astype(bool)]
    return r.groupby('dispatch_late').agg(review_count=('review_score', 'count'),
        mean_score=('review_score', 'mean'), negative_rate=('negative_review', 'mean')).reset_index()


# [IA] registro 5
def monitoring_metrics(d):
    """Critérios propostos pelo solicitante, aplicados ao último mês observado no recorte."""
    dates = pd.to_datetime(d.order_purchase_timestamp, errors='coerce')
    end = dates.max()
    if pd.isna(end):
        return pd.DataFrame(), None, None
    end = end.normalize()
    start = end - pd.Timedelta(days=29)
    window = filter_data(d, [], [], start, end)
    metrics = seller_metrics(window)
    eligible = window[window.eligible_dispatch.astype(bool)].copy()
    approved = pd.to_datetime(eligible.order_approved_at).to_numpy(dtype='datetime64[D]')
    carrier = pd.to_datetime(eligible.order_delivered_carrier_date).to_numpy(dtype='datetime64[D]')
    # Conta dias de segunda a sexta em [aprovação, despacho); não desconta feriados.
    eligible['business_days'] = np.busday_count(approved, carrier)
    days = eligible.groupby('seller_id').business_days.mean().rename('mean_business_days')
    metrics = metrics.merge(days, on='seller_id', how='left', validate='one_to_one')
    metrics['above_tad_limit'] = metrics.late_rate.gt(.10) & metrics.eligible_orders.gt(0)
    metrics['below_score_floor'] = metrics.mean_score.lt(3.8) & metrics.review_count.gt(0)
    return metrics, start, end


def selection_report(d):
    columns = ['item_count', 'sales_value', 'freight_value', 'approval_to_carrier_days',
        'dispatch_delay_days', 'transport_days', 'delivery_days', 'review_score', 'freight_share',
        'demo_sales_minmax', 'demo_sales_zscore', 'demo_status_delivered', 'demo_status_shipped', 'demo_status_other']
    x = d[columns].apply(pd.to_numeric, errors='coerce')
    variance = x.var(ddof=0)
    low = variance[variance.fillna(0).le(1e-12)].index.tolist()
    corr = x.corr()
    pairs = [{'a': a, 'b': b, 'correlation': float(corr.loc[a, b])}
        for j, a in enumerate(columns) for b in columns[j+1:]
        if pd.notna(corr.loc[a, b]) and abs(corr.loc[a, b]) >= .95]
    # Excluir derivados de demonstração evita redundância; IDs não entram na correlação.
    selected = [c for c in columns if not c.startswith('demo_') and c not in low]
    return {'low_variance': low, 'high_correlation': pairs, 'selected_analysis': selected,
            'rule': 'Filtro semântico: retirar IDs, textos e transformações redundantes; variância <= 1e-12; correlação absoluta >= 0.95 para inspeção, sem excluir métricas gerenciais.'}, corr
