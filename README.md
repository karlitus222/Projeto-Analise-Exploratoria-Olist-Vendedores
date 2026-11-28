# Olist — Análise de Vendedores Parceiros

Projeto de Ciência de Dados desenvolvido para analisar o desempenho de vendedores do marketplace brasileiro da Olist. A solução prepara os dados brutos, relaciona pedidos, itens, produtos, vendedores e avaliações, constrói uma tabela analítica e disponibiliza um dashboard interativo para investigar atrasos no despacho e seus impactos na satisfação dos clientes.

 ### Equipe
- [David Gabriel](https://github.com/DavidGabriel333) — Etapa 1: preparação das bases no notebook compartilhado.
- [Carlos Gabriel Raposo Landim](https://github.com/karlitus222) — Etapa 2: relacionamentos e tabela analítica.
- [Roger-dev-eng](https://github.com/Roger-dev-eng) — Etapa 3: análises, indicadores e pipeline.
- [Guilherme Estrela](https://github.com/guilhermeestrela10) — Etapa 4: dashboard Streamlit.

## Conteúdo

- [Descrição](#descrição)
- [Briefing e perguntas de negócio](#briefing-e-perguntas-de-negócio)
- [Links](#links)
- [Objetivo](#objetivo)
- [Funcionalidades](#funcionalidades)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar localmente](#como-executar-localmente)
- [Como executar no Google Colab](#como-executar-no-google-colab)
- [Como usar o pipeline](#como-usar-o-pipeline)
- [Dashboard](#dashboard)
- [Validação](#validação)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Cuidados metodológicos](#cuidados-metodológicos)
- [Fonte dos dados](#fonte-dos-dados)

## Descrição

O projeto utiliza o **Brazilian E-Commerce Public Dataset by Olist**, disponibilizado no Kaggle, para responder perguntas sobre a operação de vendedores parceiros. A análise considera o despacho dos pedidos, as avaliações dos clientes, o volume de vendas e os critérios de acompanhamento definidos no briefing da disciplina.

O fluxo completo combina um notebook exploratório, funções reutilizáveis de processamento e um dashboard multipágina em Streamlit. Os indicadores apresentados no painel usam a mesma lógica documentada na análise.

## Briefing e perguntas de negócio

**Briefing recebido:** analisar a operação de vendedores parceiros da Olist, relacionando o cumprimento do despacho dos pedidos à satisfação dos clientes e propondo critérios objetivos para acompanhamento da operação.

As três perguntas de negócio são:

1. **Quais vendedores mais atrasam o despacho dos pedidos?**
2. **Vendedores que atrasam recebem avaliações piores?**
3. **Que critérios objetivos a empresa poderia usar para acompanhar ou advertir vendedores?**

## Links

- **Base de dados:** [Brazilian E-Commerce Public Dataset by Olist no Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
- **Painel publicado:** [Painel no Streamlit](https://olist-vendedores-grupo04.streamlit.app/)

## Objetivo

- Preparar e validar as bases públicas da Olist.
- Relacionar pedidos, itens, produtos, vendedores e avaliações.
- Construir uma tabela analítica na granularidade vendedor–pedido.
- Medir atrasos no despacho e sua relação com avaliações.
- Identificar vendedores que atendem aos critérios de acompanhamento.
- Apresentar os resultados em um painel interativo.

## Funcionalidades

- Diagnóstico de colunas, valores ausentes, chaves, datas e valores atípicos.
- Limpeza e padronização das bases brutas.
- Sinalização de outliers de preço e frete pelo IQR, sem exclusão automática.
- Relacionamentos com validação de cardinalidade e auditoria.
- Geração da tabela analítica `tabela_vendedor_pedido.csv`.
- Codificação one-hot de estado/status e normalização MinMax/Z-score de atraso de despacho e valor total.
- Filtros por estado, categoria, vendedor e período.
- Ranking de vendedores por taxa de atraso no despacho.
- Comparação entre situação do despacho e avaliações recebidas.
- Classificação de vendedores conforme volume mínimo e limites de atraso.
- Tabelas, gráficos e download dos dados filtrados.

## Estrutura do projeto

```text
Projeto-Analise-Exploratoria-Olist-Vendedores/
├── dados_brutos/                 # CSVs originais da Olist
├── dados_tratados/               # Bases limpas e padronizadas
├── notebooks/
│   └── 01_Preparacao_Dados_Olist.ipynb
├── pipeline/
│   ├── funcoes.py                # Limpeza, relacionamentos e tabela analítica
│   ├── pipeline.py               # Orquestração do processamento
│   └── __init__.py
├── tabelas_analiticas/           # CSVs usados nas análises
├── streamlit/
│   ├── app.py                    # Entrada do dashboard
│   ├── pages/                    # Páginas das perguntas do briefing
│   └── src/                      # Carga, métricas, gráficos e apresentação
├── requirements.txt
├── uso_de_ia.md                  # Registro das contribuições assistidas
└── README.md
```

## Como executar localmente

### Pipeline e notebook

Use Python 3.11 ou superior na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O notebook pode ser aberto no Jupyter ou no VS Code. Ao executá-lo localmente, ajuste o caminho `PASTA_PROJETO` e remova ou adapte a montagem do Google Drive.

### Dashboard Streamlit

As dependências do painel ficam separadas em `streamlit/requirements.txt`:

```powershell
cd streamlit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O painel será disponibilizado, normalmente, em `http://localhost:8501`. Em execuções seguintes, dentro da pasta `streamlit/`, basta executar:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

No Linux ou macOS, substitua `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

## Como executar no Google Colab

O [notebook compartilhado da equipe](https://colab.research.google.com/drive/12h_cO8pzdXaaLIUrLwkSKLnSUY9lxdFS) contém a versão utilizada no desenvolvimento colaborativo.

1. Crie ou utilize a pasta `Projeto_Analise_Olist` no Google Drive.
2. Mantenha os arquivos de `dados_brutos/` na subpasta correspondente.
3. Abra o notebook e execute as células em ordem.
4. Autorize o acesso ao Drive quando solicitado.

Ao final do processamento, a tabela analítica é exportada para `tabelas_analiticas/tabela_vendedor_pedido.csv`.

## Como usar o pipeline

As funções principais podem ser importadas pelo pacote `pipeline`:

```python
from pipeline import preprocessar

tabela = preprocessar(
    orders,
    items,
    products,
    sellers,
    reviews,
)
```

Os argumentos devem ser DataFrames carregados dos cinco CSVs utilizados na análise. A função:

- remove duplicatas exatas e converte textos vazios em valores ausentes, sem preencher nulos com zero;
- converte datas e colunas numéricas e marca valores fora dos limites definidos como ausentes;
- sinaliza valores extremos de preço e frete pelo critério IQR, sem removê-los;
- relaciona pedidos, itens, produtos, vendedores e avaliações e calcula indicadores na granularidade vendedor–pedido;
- adiciona codificação one-hot para estado/status e versões MinMax e Z-score de atraso de despacho e valor total.

O resultado completo, mantendo também as colunas originais, é gravado em `tabelas_analiticas/tabela_vendedor_pedido.csv`.

## Dashboard

O painel multipágina apresenta:

| Página | Conteúdo |
| --- | --- |
| Visão geral | Indicadores do recorte e acesso às análises |
| Atrasos no despacho | Ranking de vendedores pela taxa de atraso |
| Atrasos e avaliações | Nota média e proporção de notas baixas por situação do despacho |
| Critérios para vendedores | Classificação baseada em volume e limites de acompanhamento |

O CSV utilizado pelo painel é `tabelas_analiticas/tabela_vendedor_pedido.csv`. Os filtros recalculam os indicadores, gráficos, tabelas e sínteses para o recorte selecionado.

## Processo de tratamento dos dados

1. **Carregamento:** leitura dos CSVs de clientes, pedidos, itens, produtos, vendedores e avaliações.
2. **Limpeza:** remoção de duplicatas exatas, conversão de textos vazios em ausentes, padronização de textos, conversão de datas e números, validação de limites e sinalização de outliers por IQR.
3. **Relacionamento:** junção das tabelas por suas chaves, com validação de cardinalidade, cobertura e duplicidades.
4. **Agregação:** avaliações são consolidadas por pedido e os itens são relacionados ao vendedor responsável.
5. **Tabela analítica:** construção de uma linha por vendedor–pedido, com indicadores de despacho, entrega, avaliação, participação de múltiplos vendedores e contagens de itens sinalizados como outliers; também inclui codificações categóricas e atributos normalizados.
6. **Análise:** cálculo das taxas de atraso, notas médias, proporção de avaliações baixas e classificações de acompanhamento.
7. **Publicação:** exportação dos CSVs analíticos e leitura da tabela final pelo dashboard, que recalcula os indicadores conforme os filtros.

## Principais desafios encontrados

- Relacionar tabelas com granularidades diferentes sem duplicar pedidos, itens ou valores financeiros.
- Definir uma unidade analítica consistente para pedidos com mais de um vendedor.
- Tratar datas ausentes, cancelamentos e casos em que o despacho não é avaliável.
- Preservar valores ausentes nas flags, sem transformá-los indevidamente em atraso ou pontualidade.
- Evitar conclusões causais a partir da comparação entre atraso e avaliação, já que os dados mostram associação.
- Manter os cálculos do notebook, pipeline e dashboard alinhados.

## Principais conclusões

- O ranking de atraso deve considerar apenas vendedores com pelo menos **20 despachos avaliáveis**, reduzindo distorções causadas por baixo volume.
- Pedidos com atraso no despacho apresentaram nota média inferior aos pedidos sem atraso: **3,67 contra 4,16** na análise original.
- A proporção de avaliações baixas também foi maior entre pedidos atrasados: **24,50% contra 12,80%**.
- A relação observada indica associação entre atraso e avaliação, mas não prova que o atraso tenha causado diretamente a nota baixa.
- Os critérios de acompanhamento usam pelo menos **20 despachos avaliáveis**, **10 pedidos com avaliação** e limite de **20%** para atraso ou avaliação baixa. Na análise original, 811 vendedores atingiram os mínimos; 591 foram classificados com algum nível de atenção.

## Validação

A validação da pipeline é feita pelo notebook `notebooks/01_Preparacao_Dados_Olist.ipynb`. Execute as células em ordem; na etapa 5, a função `preprocessar()` recebe as cinco bases brutas, exibe as contagens da tabela vendedor–pedido e mostra uma amostra do resultado, além de gravar o CSV final.

Para validar o dashboard manualmente, execute-o conforme as instruções acima e confira as páginas, filtros, tabelas e gráficos. O repositório atualmente não inclui a pasta de testes automatizados do Streamlit.

## Tecnologias utilizadas

- Python
- Pandas e NumPy
- Matplotlib e Seaborn
- Streamlit
- Altair
- Jupyter Notebook / Google Colab
- Pytest

## Cuidados metodológicos

A unidade principal da tabela analítica é **vendedor–pedido**. As avaliações são agregadas antes das junções para evitar a multiplicação de itens e valores financeiros.

Pedidos com mais de um vendedor são sinalizados. Como despacho e avaliação são informações do pedido, esses indicadores não identificam isoladamente a responsabilidade de um único vendedor.

Valores ausentes permanecem ausentes. Ao carregar o CSV, preserve as flags booleanas com `dtype` apropriado e não interprete ausência como pontualidade ou avaliação favorável.

## Fonte dos dados

Olist, [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), Kaggle. Os dados de origem e as tabelas derivadas estão sob [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), conforme a fonte.
