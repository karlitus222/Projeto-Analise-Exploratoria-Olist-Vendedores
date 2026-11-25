# Olist — gestão de vendedores parceiros

Trabalho de Ciência de Dados, período 2026/2, briefing 5. A base relaciona vendedores, itens, pedidos e avaliações para a análise posterior de despacho e satisfação.

## Equipe

- [Carlos Gabriel Raposo Landim](https://github.com/karlitus222) — partes 3 e 4: relacionamentos e tabela analítica.
- [David Gabriel](https://github.com/DavidGabriel333) — preparação das bases no notebook compartilhado.
- [Roger-dev-eng](https://github.com/Roger-dev-eng) — parte 5 e 6: realizar as análises das perguntas e desenvolver o pipeline.
- [Guilherme Estrela](https://github.com/guilhermeestrela10) - parte 7 e 8: streamlit e documentaçao.
## O que está pronto

| Etapa | Situação nesta versão |
|---|---|
| 1. Preparar o ambiente | Pastas, importações e carregamento configurados no Colab |
| 2. Conhecer e preparar as bases | Diagnóstico de colunas, ausências, chaves, datas e valores atípicos |
| 3. Relacionar as tabelas | Junções com validação de cardinalidade e auditoria |
| 4. Construir a tabela analítica | Base vendedor–pedido, indicadores e exportação dos CSVs |
| 5. Realizar as análises | Pendente |
| 6. Desenvolver o pipeline completo `preprocessar()` | Implementado em `pipeline/`; coordena limpeza, relacionamentos, tabela analítica, resumo e exportação |
| 7. Construir o Streamlit | Pendente |
| 8. Finalizar documentação e apresentação | Parcial: instruções, dicionário e verificação disponíveis |

O relatório final, o diário de decisões, as respostas às três perguntas e a apresentação serão completados pela equipe.

## Arquivos

- [`notebooks/01_Preparacao_Dados_Olist.ipynb`](notebooks/01_Preparacao_Dados_Olist.ipynb): versão integrada do Colab, com 58 células. Contém a preparação anterior e as partes 3 e 4 ao final.
- [`notebooks/02_Relacionamentos_e_Tabela_Analitica.ipynb`](notebooks/02_Relacionamentos_e_Tabela_Analitica.ipynb): apenas as partes 3 e 4, com saídas da execução local. É uma alternativa para quem já executou a preparação; depende de `dados_limpos` e `PASTA_TRATADOS`.
- [`pipeline/`](pipeline/): `pipeline.py` coordena as etapas; `funcoes.py` contém limpeza, relacionamentos, construção da tabela analítica e resumo.
- [`relacionamentos.py`](relacionamentos.py): funções reutilizáveis para o futuro pipeline.
- [`validar_relacionamentos.py`](validar_relacionamentos.py): seis testes de casos especiais.
- [`dados_brutos/`](dados_brutos): CSVs de origem usados pelo notebook.
- [`dados_tratados/`](dados_tratados): bases preparadas; as saídas das partes 3 e 4 ficam em `partes_3_4/`.
- [`docs/dicionario_tabela_analitica.csv`](docs/dicionario_tabela_analitica.csv): descrição, tipo e origem dos 46 campos da tabela principal.
- [`docs/validacao.md`](docs/validacao.md): verificações e limites de interpretação.
- [`uso_de_ia.md`](uso_de_ia.md): registro da contribuição assistida das partes 3 e 4, a complementar com os registros anteriores da equipe.

## Executar no Colab

O [notebook compartilhado da equipe](https://colab.research.google.com/drive/12h_cO8pzdXaaLIUrLwkSKLnSUY9lxdFS) contém as mesmas fontes do notebook integrado deste repositório.

1. No Google Drive, use a pasta `Projeto_Analise_Olist`, com os arquivos de `dados_brutos/` dentro da subpasta de mesmo nome.
2. Abra o notebook integrado e execute as células em ordem. A montagem do Drive solicita autorização da conta usada no Colab.
3. Os resultados são gravados em `Projeto_Analise_Olist/dados_tratados/`. As partes 3 e 4 usam a subpasta `partes_3_4/`.

O notebook integrado contém o código salvo no Colab. As células acrescentadas foram testadas localmente, mas ainda não foram executadas no ambiente remoto. O segundo notebook preserva as saídas desse teste local.

## Usar as funções localmente

```bash
python -m pip install -r requirements.txt
python -m unittest validar_relacionamentos -v
```

```python
from pipeline import preprocessar, resumir_vendedores

# As cinco variáveis são DataFrames carregados dos CSVs brutos.
tabela = preprocessar(orders, items, products, sellers, reviews)
resumo = resumir_vendedores(tabela)
```

A pipeline salva a tabela analítica e o resumo em `tabelas_analiticas/`.

Para abrir o notebook em Jupyter local, adapte a montagem do Drive e o caminho `PASTA_PROJETO` às pastas da máquina.

## Cuidados com a base

A unidade da tabela principal é **vendedor–pedido**. As avaliações são agregadas antes das junções, evitando multiplicar itens e valores financeiros. Pedidos com mais de um vendedor são sinalizados: despacho e avaliação são informações do pedido e não identificam, isoladamente, a responsabilidade de cada vendedor.

Campos sem informação permanecem ausentes. Ao ler o CSV, preserve as flags com `dtype={'flag_atraso_despacho': 'boolean', 'flag_atraso_entrega': 'boolean', 'flag_nota_baixa': 'boolean'}`. Não transforme ausência em pontualidade ou avaliação favorável.

## Fonte dos dados

Olist, [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), Kaggle. Os dados de origem e as tabelas derivadas estão sob [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), conforme a fonte. Atribuição e descrição das transformações em [`docs/origem_dos_dados.md`](docs/origem_dos_dados.md).
