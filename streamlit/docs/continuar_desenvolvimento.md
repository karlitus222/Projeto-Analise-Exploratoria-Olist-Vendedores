# Continuar o desenvolvimento do Streamlit

Responsável pela etapa 7: Guilherme Estrela. Versão da demonstração de 27/11/2026.

Esta pasta é independente. A publicação acrescenta somente `streamlit/`; não altera os notebooks, o pipeline, as tabelas analíticas nem a documentação da raiz do repositório.

[Voltar ao painel](../README.md) · [Índice da documentação](README.md)

## Executar depois de clonar o repositório

No terminal, entrar na pasta `streamlit` e usar Python 3.11. Criar um ambiente próprio evita conflito com as dependências das outras etapas.

```powershell
cd streamlit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

No Linux ou macOS, usar `.venv/bin/python` no lugar de `.\.venv\Scripts\python.exe`.

Abrir o endereço mostrado no terminal. Para testar, ainda dentro de `streamlit/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

O painel lê seu CSV incluído e não precisa executar o pipeline nem baixar dados do Kaggle para iniciar.

## Onde ajustar cada parte

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Entrada da visão geral; chama a interface compartilhada |
| `pages/` | Entrada das três páginas do briefing |
| `src/dashboard.py` | Filtros, indicadores, tabelas, navegação e organização das páginas |
| `src/analysis.py` | Cálculos sobre os dados filtrados |
| `src/visualizations.py` | Gráficos Altair, detalhes, destaque e zoom |
| `src/presentation.py` | Nome fictício do vendedor e conclusões calculadas |
| `data/processed/tabela_analitica.csv` | Base da versão demonstrada |
| `tests/test_dashboard.py` | Testes dos filtros e dos dados exibidos nas quatro páginas |
| `.streamlit/config.toml` | Tema e opções do Streamlit |

## Como uma página recebe os dados

`app.py` ou um arquivo de `pages/` chama `render()` em `src/dashboard.py`. A interface lê o CSV, aplica os filtros e passa esse recorte para `src/analysis.py`. As tabelas usam esses resultados; os gráficos são montados em `src/visualizations.py`, e as conclusões em `src/presentation.py`. Ao mudar uma regra, confira os três resultados: indicadores, tabelas e gráficos/conclusões.

Para alterar somente a interface, mantenha a base incluída e execute os testes. Para integrar o pipeline, siga a seção abaixo antes de trocar o CSV.

## Base desta versão e integração com o pipeline da equipe

A versão demonstrada usa uma cópia do CSV final do projeto anterior de Guilherme: `data/processed/tabela_analitica.csv`, com 41 colunas. A origem e o SHA256 estão em `docs/origem_da_base.json`.

O repositório dos colaboradores, no commit `05a8c34`, usa `tabelas_analiticas/tabela_vendedor_pedido.csv`, com 46 colunas e outro contrato de dados. Esses arquivos não são intercambiáveis. Esta publicação mantém o comportamento demonstrado; ela não adapta silenciosamente as regras do pipeline dos colegas.

Antes de integrar a saída do pipeline, conferir granularidade, duplicações, tipos e regras de cada campo. Alguns exemplos que exigem conferência:

| Painel atual | Campo do pipeline a examinar |
|---|---|
| `dispatch_late` | `flag_atraso_despacho` |
| `dispatch_delay_days` | `diferenca_despacho_dias` / `atraso_despacho_dias` |
| `eligible_dispatch` | `despacho_avaliavel`, `pedido_multivendedor` e campos de cronologia |
| `review_score` | `nota_media_pedido`, quantidade e regra de agregação das avaliações |
| `eligible_review` | `avaliacao_encontrada`, avaliações válidas e elegibilidade do pedido |
| `purchase_month` | `mes_compra` |
| `sales_value` / `freight_value` | `valor_produtos` / `valor_frete` |

A tabela acima é um roteiro de conferência, não uma equivalência automática. Não basta renomear colunas: o painel usa avaliação única por pedido e regras explícitas para pedidos multivendedor. Flags ausentes não devem virar pontualidade, e ausência de nota não deve virar nota zero.

Depois de definir o contrato com a equipe, ajustar a leitura em `src/dashboard.py`, os cálculos em `src/analysis.py`, as conclusões e os testes antes de substituir a base desta versão.

## Comportamento atual dos filtros

- UF fixa em PI, conforme a demonstração solicitada.
- Todos os anos mostra o total disponível do PI. A base incluída tem apenas 2018: 12 pedidos, um vendedor, 11 despachos elegíveis e 11 avaliações elegíveis.
- Trocar o ano restaura todos os meses e o calendário anual completo.
- Janeiro a dezembro estão disponíveis. Mês e período alteram os indicadores, as tabelas, os gráficos e as conclusões.
- Junho e setembro a dezembro não têm pedidos do PI nesta base. O painel mostra 0 pedidos, taxa sem dados e uma explicação. Não há pedidos sintéticos.
- Os filtros permanecem ao trocar de página. O volume mínimo limita o ranking; os controles do simulador alteram somente o cenário identificado na tela.
- Loja Aurora é um nome fictício. O ID real continua disponível.

Os testes dependem desse recorte e do CSV incluído. Ao liberar outros estados ou trocar a base, atualizar também as expectativas dos testes e os textos que mencionam PI.

## Publicação e compartilhamento

Os executáveis, ambientes virtuais, logs, caches e credenciais da máquina não fazem parte desta entrega. Para demonstração temporária, consultar `docs/compartilhamento.md`.

O envio desta pasta ao GitHub não cria nem atualiza automaticamente uma hospedagem Streamlit. Um colaborador pode executar o painel localmente ou configurar uma hospedagem separada.

Fonte dos dados: Olist / Kaggle, sob CC BY-NC-SA 4.0, conforme a fonte indicada no README da raiz. O histórico de assistência desta etapa está em `uso_de_ia.md` nesta pasta.
