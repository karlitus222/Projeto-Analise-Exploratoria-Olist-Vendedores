import pandas as pd

# [IA] registro 1 do complemento das partes 3 e 4.


def conferir_chave(df, colunas, nome):
    if df[colunas].isna().any().any():
        raise ValueError(f'{nome}: há valores ausentes na chave {colunas}.')
    if df.duplicated(colunas).any():
        raise ValueError(f'{nome}: há chaves repetidas com dados diferentes em {colunas}.')


def relacionar_tabelas(dados_limpos):
    chaves = {
        'orders': ['order_id'],
        'items': ['order_id', 'order_item_id'],
        'products': ['product_id'],
        'sellers': ['seller_id'],
    }
    obrigatorias = set(chaves) | {'reviews'}
    faltantes = obrigatorias - set(dados_limpos)
    if faltantes:
        raise ValueError(f'Bases não carregadas: {sorted(faltantes)}')

    bases = {}
    duplicatas = []
    for nome in sorted(obrigatorias):
        df = dados_limpos[nome].copy()
        repetidas = int(df.duplicated().sum())
        bases[nome] = df.drop_duplicates().copy()
        duplicatas.append({'base': nome, 'linhas_entrada': len(df),
                           'duplicatas_completas': repetidas,
                           'linhas_utilizadas': len(bases[nome])})

    for nome, colunas in chaves.items():
        conferir_chave(bases[nome], colunas, nome)
    for coluna in ['order_id', 'seller_id', 'product_id']:
        if bases['items'][coluna].isna().any():
            raise ValueError(f'items: há valores ausentes em {coluna}.')

    orders, items = bases['orders'], bases['items']
    products, sellers = bases['products'], bases['sellers']
    reviews = bases['reviews']
    for coluna in ['order_purchase_timestamp', 'order_approved_at',
                   'order_delivered_carrier_date', 'order_delivered_customer_date',
                   'order_estimated_delivery_date']:
        orders[coluna] = pd.to_datetime(orders[coluna], format='mixed', errors='coerce')
    items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'], format='mixed', errors='coerce')

    # review_id não é uma chave única global. A agregação é feita por pedido.
    reviews['review_score'] = pd.to_numeric(reviews['review_score'], errors='coerce')
    reviews['nota_valida'] = reviews['review_score'].where(reviews['review_score'].isin([1, 2, 3, 4, 5]))
    reviews['nota_baixa'] = reviews['nota_valida'].le(2) & reviews['nota_valida'].notna()
    avaliacoes = reviews.dropna(subset=['order_id']).groupby('order_id', as_index=False).agg(
        qtd_avaliacoes_pedido=('review_id', 'size'),
        qtd_avaliacoes_validas=('nota_valida', 'count'),
        nota_media_pedido=('nota_valida', 'mean'),
        menor_nota_pedido=('nota_valida', 'min'),
        maior_nota_pedido=('nota_valida', 'max'),
        qtd_avaliacoes_baixas_pedido=('nota_baixa', 'sum'),
    )
    conferir_chave(avaliacoes, ['order_id'], 'avaliações agregadas')

    # Contagens calculadas antes dos merges, para não depender de linhas multiplicadas.
    vendedores_por_pedido = items.groupby('order_id')['seller_id'].nunique()
    base_itens = items.copy()
    base_itens['qtd_vendedores_pedido'] = base_itens['order_id'].map(vendedores_por_pedido)
    historico_merges = []
    for nome, direita, chave, indicador in [
        ('items + orders', orders, 'order_id', 'pedido_encontrado'),
        ('items + products', products, 'product_id', 'produto_encontrado'),
        ('items + sellers', sellers, 'seller_id', 'vendedor_encontrado'),
        ('items + avaliações agregadas', avaliacoes, 'order_id', 'avaliacao_encontrada'),
    ]:
        antes = len(base_itens)
        base_itens = base_itens.merge(direita, on=chave, how='left', validate='many_to_one', indicator=True)
        sem_correspondencia = int(base_itens['_merge'].eq('left_only').sum())
        base_itens[indicador] = base_itens['_merge'].eq('both')
        base_itens = base_itens.drop(columns='_merge')
        historico_merges.append({'relacionamento': nome, 'chave': chave,
                                 'linhas_antes': antes, 'linhas_depois': len(base_itens),
                                 'itens_sem_correspondencia': sem_correspondencia})
        assert len(base_itens) == antes, f'O merge {nome} alterou a quantidade de itens.'

    conferir_chave(base_itens, ['order_id', 'order_item_id'], 'base de itens relacionada')
    auditoria = {
        'duplicatas': pd.DataFrame(duplicatas),
        'merges': pd.DataFrame(historico_merges),
        'pedidos_sem_itens': int((~orders['order_id'].isin(items['order_id'])).sum()),
        'pedidos_com_multiplas_avaliacoes': int(avaliacoes['qtd_avaliacoes_pedido'].gt(1).sum()),
        'reviews_sem_order_id': int(reviews['order_id'].isna().sum()),
        'reviews_sem_pedido_cadastrado': int((reviews['order_id'].notna() & ~reviews['order_id'].isin(orders['order_id'])).sum()),
        'notas_invalidas_ou_ausentes': int(reviews['nota_valida'].isna().sum()),
    }
    return base_itens, auditoria


def construir_tabela_analitica(base_itens):
    itens = base_itens.copy()
    compra = itens['order_purchase_timestamp']
    despacho = itens['order_delivered_carrier_date']
    prazo = itens['shipping_limit_date']
    itens['despacho_antes_compra'] = despacho.notna() & compra.notna() & despacho.lt(compra)
    itens['prazo_antes_compra'] = prazo.notna() & compra.notna() & prazo.lt(compra)
    itens['prazo_item_valido'] = compra.notna() & prazo.notna() & prazo.ge(compra)
    itens['prazo_item_analise'] = prazo.where(itens['prazo_item_valido'])
    itens['item_despacho_avaliavel'] = (
        itens['prazo_item_valido'] & despacho.notna() & despacho.ge(compra)
        & itens['pedido_encontrado'] & ~itens['order_status'].isin(['canceled', 'unavailable'])
    )
    itens['item_atrasado'] = itens['item_despacho_avaliavel'] & despacho.gt(prazo)
    itens['categoria_analise'] = itens['product_category_name'].fillna('sem_categoria')

    # Cada linha passa a representar um vendedor dentro de um pedido.
    campos_pedido = [
        'order_status', 'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date', 'seller_city', 'seller_state',
        'qtd_vendedores_pedido', 'nota_media_pedido', 'menor_nota_pedido',
        'maior_nota_pedido', 'qtd_avaliacoes_pedido', 'qtd_avaliacoes_validas',
        'qtd_avaliacoes_baixas_pedido', 'pedido_encontrado', 'vendedor_encontrado',
        'avaliacao_encontrada',
    ]
    agregacoes = {campo: (campo, 'first') for campo in campos_pedido}
    agregacoes.update({
        'qtd_itens': ('order_item_id', 'size'),
        'qtd_produtos_distintos': ('product_id', 'nunique'),
        'valor_produtos': ('price', lambda s: s.sum(min_count=1)),
        'valor_frete': ('freight_value', lambda s: s.sum(min_count=1)),
        'prazo_despacho_vendedor': ('prazo_item_analise', 'min'),
        'ultimo_prazo_despacho_vendedor': ('prazo_item_analise', 'max'),
        'qtd_itens_prazo_valido': ('prazo_item_valido', 'sum'),
        'qtd_itens_despacho_avaliavel': ('item_despacho_avaliavel', 'sum'),
        'qtd_itens_atrasados': ('item_atrasado', 'sum'),
        'qtd_itens_sem_produto': ('produto_encontrado', lambda s: (~s).sum()),
        'qtd_categorias': ('categoria_analise', 'nunique'),
        'categorias': ('categoria_analise', lambda s: '|'.join(sorted(s.unique()))),
        'despacho_antes_compra': ('despacho_antes_compra', 'max'),
        'prazo_antes_compra': ('prazo_antes_compra', 'max'),
    })
    tabela = itens.groupby(['seller_id', 'order_id'], as_index=False).agg(**agregacoes)
    tabela['valor_total'] = tabela['valor_produtos'] + tabela['valor_frete']
    tabela['pedido_multivendedor'] = tabela['qtd_vendedores_pedido'].gt(1)
    tabela['mes_compra'] = tabela['order_purchase_timestamp'].dt.strftime('%Y-%m')

    tabela['despacho_avaliavel'] = tabela['qtd_itens_despacho_avaliavel'].eq(tabela['qtd_itens'])
    diferenca_despacho = (
        tabela['order_delivered_carrier_date'] - tabela['prazo_despacho_vendedor']
    ).dt.total_seconds() / 86400
    tabela['diferenca_despacho_dias'] = diferenca_despacho.where(tabela['despacho_avaliavel'])
    tabela['atraso_despacho_dias'] = tabela['diferenca_despacho_dias'].clip(lower=0)
    tabela['flag_atraso_despacho'] = tabela['qtd_itens_atrasados'].gt(0).astype('boolean')
    tabela.loc[~tabela['despacho_avaliavel'], 'flag_atraso_despacho'] = pd.NA

    entrega = tabela['order_delivered_customer_date']
    estimativa = tabela['order_estimated_delivery_date']
    tabela['entrega_avaliavel'] = (
        tabela['order_status'].eq('delivered') & entrega.notna() & estimativa.notna()
        & tabela['order_purchase_timestamp'].notna()
        & entrega.ge(tabela['order_purchase_timestamp'])
        & estimativa.ge(tabela['order_purchase_timestamp'].dt.normalize())
    )
    # A previsão de entrega é uma data: a hora do recebimento no mesmo dia não é atraso.
    tabela['diferenca_entrega_dias'] = (entrega.dt.normalize() - estimativa.dt.normalize()).dt.days.where(tabela['entrega_avaliavel'])
    tabela['atraso_entrega_dias'] = tabela['diferenca_entrega_dias'].clip(lower=0)
    tabela['flag_atraso_entrega'] = tabela['diferenca_entrega_dias'].gt(0).astype('boolean')
    tabela.loc[~tabela['entrega_avaliavel'], 'flag_atraso_entrega'] = pd.NA

    # Flags sem informação permanecem ausentes, em vez de virar avaliações favoráveis.
    tabela['flag_nota_baixa'] = tabela['nota_media_pedido'].le(2).astype('boolean')
    tabela.loc[tabela['nota_media_pedido'].isna(), 'flag_nota_baixa'] = pd.NA
    conferir_chave(tabela, ['seller_id', 'order_id'], 'tabela analítica')
    assert tabela['qtd_itens'].sum() == len(base_itens)
    assert len(tabela) == len(base_itens[['seller_id', 'order_id']].drop_duplicates())
    return tabela


def resumir_vendedores(tabela_analitica):
    resumo = tabela_analitica.groupby('seller_id', as_index=False).agg(
        seller_state=('seller_state', 'first'),
        qtd_pedidos=('order_id', 'nunique'),
        qtd_itens=('qtd_itens', 'sum'),
        pedidos_despacho_avaliavel=('despacho_avaliavel', 'sum'),
        pedidos_com_atraso_despacho=('flag_atraso_despacho', 'sum'),
        atraso_medio_despacho_dias=('atraso_despacho_dias', 'mean'),
        pedidos_com_nota=('nota_media_pedido', 'count'),
        nota_media=('nota_media_pedido', 'mean'),
        pedidos_nota_baixa=('flag_nota_baixa', 'sum'),
        pedidos_multivendedor=('pedido_multivendedor', 'sum'),
    )
    resumo['taxa_atraso_despacho_pct'] = 100 * resumo['pedidos_com_atraso_despacho'] / resumo['pedidos_despacho_avaliavel'].replace(0, float('nan'))
    resumo['taxa_nota_baixa_pct'] = 100 * resumo['pedidos_nota_baixa'] / resumo['pedidos_com_nota'].replace(0, float('nan'))
    return resumo
