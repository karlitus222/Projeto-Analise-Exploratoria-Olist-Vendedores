import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from relacionamentos import relacionar_tabelas, construir_tabela_analitica, resumir_vendedores


def bases_exemplo():
    orders = pd.DataFrame({
        'order_id': ['p1', 'p2', 'p3'],
        'order_status': ['delivered', 'processing', 'canceled'],
        'order_purchase_timestamp': ['2018-01-01', '2018-01-01', '2018-01-01'],
        'order_approved_at': ['2018-01-01', '2018-01-01', '2018-01-01'],
        'order_delivered_carrier_date': ['2018-01-03 12:00', None, '2018-01-03'],
        'order_delivered_customer_date': ['2018-01-05 22:00', None, None],
        'order_estimated_delivery_date': ['2018-01-05', '2018-01-05', '2018-01-05'],
    })
    items = pd.DataFrame({
        'order_id': ['p1', 'p1', 'p1', 'p2', 'p3'],
        'order_item_id': [1, 2, 3, 1, 1],
        'product_id': ['a', 'a', 'b', 'b', 'a'],
        'seller_id': ['v1', 'v1', 'v2', 'v1', 'v2'],
        'shipping_limit_date': ['2018-01-03', '2018-01-04', '2018-01-04', '2018-01-03', '2018-01-02'],
        'price': [10.0, 10.0, 30.0, 20.0, 40.0],
        'freight_value': [2.0, 2.0, 3.0, 4.0, 5.0],
    })
    products = pd.DataFrame({'product_id': ['a', 'b'], 'product_category_name': ['papelaria', None]})
    sellers = pd.DataFrame({'seller_id': ['v1', 'v2'], 'seller_city': ['teresina', 'fortaleza'], 'seller_state': ['PI', 'CE']})
    reviews = pd.DataFrame({'review_id': ['r1', 'r2', 'r1'], 'order_id': ['p1', 'p1', 'p3'], 'review_score': [1, 5, 2]})
    return {'orders': orders, 'items': items, 'products': products, 'sellers': sellers, 'reviews': reviews}


class TestRelacionamentos(unittest.TestCase):
    def montar(self, dados=None):
        base, auditoria = relacionar_tabelas(dados or bases_exemplo())
        return base, construir_tabela_analitica(base), auditoria

    def test_avaliacoes_nao_multiplicam_itens_ou_valores(self):
        base, tabela, auditoria = self.montar()
        self.assertEqual(len(base), 5)
        self.assertEqual(len(tabela), 4)
        self.assertEqual(tabela.valor_produtos.sum(), 110)
        self.assertEqual(tabela.valor_frete.sum(), 16)
        linha = tabela.set_index(['seller_id', 'order_id']).loc[('v1', 'p1')]
        self.assertEqual(linha.qtd_itens, 2)
        self.assertEqual(linha.nota_media_pedido, 3)
        self.assertEqual(linha.qtd_avaliacoes_pedido, 2)
        self.assertTrue(linha.pedido_multivendedor)
        self.assertEqual(auditoria['pedidos_com_multiplas_avaliacoes'], 1)

    def test_atraso_fracionario_e_prazo_por_vendedor(self):
        _, tabela, _ = self.montar()
        tabela = tabela.set_index(['seller_id', 'order_id'])
        self.assertAlmostEqual(tabela.loc[('v1', 'p1'), 'atraso_despacho_dias'], 0.5)
        self.assertTrue(tabela.loc[('v1', 'p1'), 'flag_atraso_despacho'])
        self.assertFalse(tabela.loc[('v2', 'p1'), 'flag_atraso_despacho'])
        self.assertFalse(tabela.loc[('v1', 'p1'), 'flag_atraso_entrega'])

    def test_sem_data_e_cancelamento_nao_viram_pontualidade(self):
        _, tabela, _ = self.montar()
        tabela = tabela.set_index(['seller_id', 'order_id'])
        self.assertTrue(pd.isna(tabela.loc[('v1', 'p2'), 'flag_atraso_despacho']))
        self.assertTrue(pd.isna(tabela.loc[('v2', 'p3'), 'flag_atraso_despacho']))
        self.assertTrue(pd.isna(tabela.loc[('v1', 'p2'), 'flag_nota_baixa']))
        resumo = resumir_vendedores(tabela.reset_index()).set_index('seller_id')
        self.assertEqual(resumo.loc['v1', 'pedidos_despacho_avaliavel'], 1)

    def test_recorte_preserva_itens_sem_dimensao(self):
        dados = bases_exemplo()
        dados['orders'] = dados['orders'].iloc[:0]
        dados['products'] = dados['products'].iloc[:0]
        dados['sellers'] = dados['sellers'].iloc[:0]
        base, tabela, auditoria = self.montar(dados)
        self.assertEqual(len(base), 5)
        self.assertEqual(len(tabela), 4)
        self.assertFalse(tabela.despacho_avaliavel.any())
        self.assertFalse(base.pedido_encontrado.any())
        self.assertEqual(auditoria['merges'].iloc[0].itens_sem_correspondencia, 5)

    def test_duplicata_completa_removida_e_conflito_recusado(self):
        dados = bases_exemplo()
        dados['items'] = pd.concat([dados['items'], dados['items'].iloc[[0]]], ignore_index=True)
        base, _, _ = self.montar(dados)
        self.assertEqual(len(base), 5)
        dados['items'].loc[len(dados['items']) - 1, 'price'] = 999
        with self.assertRaisesRegex(ValueError, 'chaves repetidas'):
            self.montar(dados)

    def test_ordem_das_linhas_e_dados_originais_preservados(self):
        dados = bases_exemplo()
        copia = {nome: df.copy(deep=True) for nome, df in dados.items()}
        _, normal, _ = self.montar(dados)
        _, embaralhada, _ = self.montar({nome: df.sample(frac=1, random_state=7) for nome, df in dados.items()})
        assert_frame_equal(normal, embaralhada)
        for nome in dados:
            assert_frame_equal(dados[nome], copia[nome])


if __name__ == '__main__':
    unittest.main(verbosity=2)
