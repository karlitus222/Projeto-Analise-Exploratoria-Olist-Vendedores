"""Nomes demonstrativos e sínteses calculadas para o recorte exibido."""
# [IA] registro 13
from .analysis import review_comparison, monitoring_metrics

SELLER_NAMES = {'47efca563408aae19bb7206c2d969ea9': 'Loja Aurora'}


def seller_name(seller_id):
    return SELLER_NAMES.get(str(seller_id), 'Loja ' + str(seller_id)[:8])


def named_metrics(metrics):
    result = metrics.copy()
    result['seller_name'] = result.seller_id.map(seller_name)
    return result


def business_summary(page, data, metrics):
    if data.empty:
        return ('O período selecionado tem 0 pedidos registrados na base do PI. '
                'Sem registros, não é possível avaliar atrasos, satisfação ou critérios de acompanhamento. '
                'Isso indica ausência de dados neste recorte, e não comprova ausência de vendas fora desta base.')
    eligible = data[data.eligible_dispatch]
    count = len(eligible)
    late = int(eligible.dispatch_late.sum())
    if page == 'atrasos':
        if not count:
            return 'Não há despachos elegíveis neste recorte para avaliar o cumprimento dos prazos.'
        rate = f'{late / count:.1%}'.replace('.', ',')
        names = ', '.join(metrics.seller_id.map(seller_name))
        return (f'No recorte do PI, {names} reúne {count} despachos elegíveis, com {late} atrasos ({rate}). '
                'Há somente um vendedor nesta base do estado; não é possível comparar parceiros. '
                'O resultado descreve esta amostra e não comprova o desempenho de todos os vendedores do Piauí.')
    if page == 'avaliacoes':
        reviewed = data[data.eligible_review]
        if reviewed.empty:
            return 'Não há avaliações elegíveis neste recorte para analisar a satisfação dos clientes.'
        mean = f'{reviewed.review_score.mean():.2f}'.replace('.', ',')
        groups = review_comparison(data)
        if len(groups) < 2:
            return (f'A nota média é {mean}, calculada em {len(reviewed)} pedidos avaliados. '
                    'Não é possível comparar avaliações de despachos com e sem atraso, pois o recorte não contém os dois grupos. '
                    'Não podemos concluir, a partir desta amostra, que atrasos provocam notas piores.')
        return (f'O recorte contém {len(reviewed)} pedidos avaliados e nota média {mean}. '
                'A tabela e o gráfico comparam os grupos com e sem atraso. Essa comparação é descritiva e não prova causalidade.')
    if page == 'criterios':
        recent, start, end = monitoring_metrics(data)
        if recent.empty:
            return 'Não há registros suficientes na janela histórica para calcular os critérios de acompanhamento.'
        tad = int(recent.above_tad_limit.sum())
        score = int(recent.below_score_floor.sum())
        orders = int(recent.eligible_orders.sum())
        dispatch_label = 'despacho elegível' if orders == 1 else 'despachos elegíveis'
        return (f'Na janela de {start:%d/%m/%Y} a {end:%d/%m/%Y}, há {orders} {dispatch_label}: '
                f'{tad} vendedores acima de 10% de atraso e {score} com nota média abaixo de 3,8. '
                'Esses critérios servem para acompanhamento. A amostra é pequena e os registros devem ser conferidos antes de qualquer advertência.')
    return (f'Este recorte reúne {data.order_id.nunique()} pedidos do PI e {metrics.seller_id.nunique()} vendedor. '
            'Os nomes exibidos são fictícios e servem apenas à demonstração. '
            'Use os filtros e os gráficos para examinar os registros; os IDs originais continuam disponíveis nas tabelas e nos detalhes.')
