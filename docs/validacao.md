# Verificação das partes 3 e 4

Fonte: arquivos CSV originais do Olist Brazilian E-Commerce Dataset, baixados do Kaggle.
Notebook de referência: 01_Preparacao_Dados_Olist.ipynb, Google Colab compartilhado pela equipe.

Execução verificada:
- As 43 células presentes na versão mais recente do Colab foram preservadas. A diferença em relação à primeira cópia era uma célula vazia adicionada pelo colega.
- Foram acrescentadas 15 células: nove de código e seis de texto.
- A cópia local de teste executou o notebook completo sem saídas de erro. Apenas a montagem do Drive e o caminho das pastas foram adaptados no teste local.
- As seis verificações de casos especiais passaram.

Dimensões das bases usadas:
orders: 99.441 linhas
items: 112.650 linhas
products: 32.951 linhas
sellers: 3.095 linhas
reviews: 99.224 linhas

Resultados de estrutura:
- Itens relacionados: 112.650 linhas.
- Tabela analítica vendedor-pedido: 100.010 linhas e 46 colunas.
- Pedidos distintos na tabela analítica: 98.666.
- Vendedores distintos: 3.095.
- Pedidos com mais de um vendedor: 1.278.
- Pedidos com mais de uma avaliação na base de avaliações: 547.
- Itens sem correspondência em pedidos, produtos ou vendedores: zero.
- Itens sem avaliação associada: 942.
- Pares vendedor-pedido sem nota: 763.
- Pedidos cadastrados sem itens: 775; ficam contados na auditoria e não são inventados na base de vendedores.

Conservação dos valores:
- Soma de price antes e depois das junções/agregação: R$ 13.591.643,70.
- Soma de freight_value antes e depois: R$ 2.251.909,54.
- Não há chave seller_id + order_id duplicada na tabela final.
- As contagens não foram fixadas no código; os valores acima descrevem a base completa usada nesta verificação.

Casos especiais verificados:
1. Avaliações múltiplas não multiplicam itens nem dinheiro.
2. Atrasos inferiores a um dia e prazos diferentes por vendedor são preservados.
3. Data ausente, cancelamento e falta de nota não viram registros favoráveis.
4. Um recorte sem algumas dimensões mantém os itens e sinaliza a falta de correspondência.
5. Cópias completas são removidas, mas chaves repetidas com dados conflitantes interrompem a junção.
6. Embaralhar as linhas não muda o resultado; os DataFrames de entrada permanecem inalterados.

A validação estrutural não é uma conclusão de negócio e não prova que uma eventual avaliação baixa tenha sido causada pelo vendedor. As perguntas do briefing e as decisões de acompanhamento devem ser analisadas pela equipe.

As fontes das 43 células anteriores foram preservadas. As 15 novas foram comparadas com o conteúdo testado e a leitura do arquivo salvo no Colab confirmou a integração. Os testes e os CSVs foram executados localmente; as células novas não foram executadas no ambiente remoto.
