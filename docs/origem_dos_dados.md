# Origem e transformações dos dados

Fonte: Olist, **Brazilian E-Commerce Public Dataset by Olist**, disponível no [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Arquivos obtidos em 23/11/2026.

Licença informada pela fonte: [Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). A atribuição à Olist e essa licença se aplicam aos dados de origem e às tabelas derivadas deste repositório.

| Arquivo bruto | Registros sem cabeçalho | Uso |
|---|---:|---|
| `olist_orders_dataset.csv` | 99.441 | Status e datas dos pedidos |
| `olist_order_items_dataset.csv` | 112.650 | Itens, vendedores, produtos, prazos e valores |
| `olist_products_dataset.csv` | 32.951 | Cadastro de produtos |
| `olist_sellers_dataset.csv` | 3.095 | Cadastro de vendedores |
| `olist_order_reviews_dataset.csv` | 99.224 | Avaliações dos pedidos |
| `olist_customers_dataset.csv` | 99.441 | Mantido por dependência da preparação anterior da equipe |

As partes 3 e 4 utilizam apenas as cinco primeiras bases. A tabela de clientes já fazia parte da preparação e não participa das junções do briefing 5.

Os arquivos em `dados_brutos/` preservam os bytes obtidos na fonte. A preparação produz cópias tratadas e sinalizações de cronologia. As partes 3 e 4 retiram cópias completas, validam chaves, agregam avaliações por pedido, relacionam as tabelas e constroem os níveis item, vendedor–pedido e resumo por vendedor. As auditorias registram cobertura, duplicatas e conservação dos valores. As transformações estão nos notebooks e em `relacionamentos.py`.

A tabela analítica resultante tem 100.010 pares vendedor–pedido e 46 colunas. Todos os CSVs publicados têm menos de 100 MB por arquivo.
