# Painel Streamlit — vendedores Olist

**Responsável:** Guilherme Estrela · Etapa 7 · Grupo 04 · Briefing 5.

Esta pasta contém a versão demonstrada em 27/11/2026: painel, CSV utilizado, dependências e testes. As outras etapas do grupo permanecem fora desta pasta.

## Comece aqui

1. **Para abrir o painel:** siga os comandos abaixo.
2. **Para mudar filtros, gráficos ou textos:** consulte o mapa de arquivos desta página.
3. **Para conectar a base do pipeline da equipe:** leia primeiro o [guia de continuidade](docs/continuar_desenvolvimento.md#base-desta-versão-e-integração-com-o-pipeline-da-equipe).
4. **Para consultar origem dos dados e verificações:** abra o [índice da documentação](docs/README.md).

## Rodar no computador

Depois de clonar o repositório, abra o terminal na raiz dele. Use **Python 3.11**:

```powershell
cd streamlit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço mostrado no terminal. Para encerrar, pressione `Ctrl+C`. Nas próximas vezes, execute apenas o último comando, dentro de `streamlit/`.

No Linux ou macOS, substitua `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

Use o ambiente virtual e o `requirements.txt` **desta pasta**. As dependências da raiz pertencem às outras etapas.

## Onde mexer

| Quero ajustar… | Arquivo |
|---|---|
| Filtros, indicadores, tabelas ou organização das páginas | [src/dashboard.py](src/dashboard.py) |
| Gráficos e suas interações | [src/visualizations.py](src/visualizations.py) |
| Conclusões e nome fictício do vendedor | [src/presentation.py](src/presentation.py) |
| Fórmulas e regras das métricas | [src/analysis.py](src/analysis.py) |
| Tema e opções de aparência | [.streamlit/config.toml](.streamlit/config.toml) |
| Dados da demonstração | [data/processed/tabela_analitica.csv](data/processed/tabela_analitica.csv) |
| Verificação automática do painel | [tests/test_dashboard.py](tests/test_dashboard.py) |

`app.py` e os três arquivos de `pages/` são as entradas das páginas. Eles chamam a interface compartilhada em `src/dashboard.py`; os filtros não precisam ser alterados em quatro arquivos separados.

## O que existe em cada aba

| Aba | Conteúdo |
|---|---|
| Visão geral | Indicadores, gráfico mensal e tabela mensal |
| Atrasos no despacho | Ranking por vendedor, volume mínimo e evolução mensal |
| Atrasos e avaliações | Notas por situação do despacho, gráfico de vendedores e tabelas |
| Critérios de acompanhamento | Janela histórica de 30 dias, gráfico, tabela e simulador |

Os filtros recalculam os dados exibidos e permanecem ao trocar de página. Trocar o ano restaura todos os meses e o período anual completo. Janeiro a dezembro estão disponíveis. Gráficos têm detalhes e zoom; tabelas permitem consulta, ordenação e download. O zoom não altera os indicadores, e o simulador altera somente o cenário identificado.

## Atenção à base de dados

O painel lê **`streamlit/data/processed/tabela_analitica.csv`**, uma cópia da base da demonstração, com 41 colunas. Ele **ainda não lê** `tabelas_analiticas/tabela_vendedor_pedido.csv`, a saída de 46 colunas do pipeline dos colaboradores. A integração exige conferir os campos e as regras; o [guia de continuidade](docs/continuar_desenvolvimento.md) explica os pontos de adaptação.

O recorte atual é fixo em **PI**: 12 pedidos de 2018, um vendedor, 11 despachos elegíveis e 11 avaliações. Por isso, “Todos os anos” e “2018” têm o mesmo total. Junho e setembro a dezembro não têm registros; o painel mostra 0 pedidos e explica a ausência. Loja Aurora é um nome fictício, com o ID original preservado.

## Conferir antes de publicar uma alteração

Dentro de `streamlit/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

A última validação da aplicação passou nos **22 testes**. Depois de alterar a base ou liberar outras UFs, atualize também as expectativas dos testes e as conclusões. Confira a troca de mês e de página no navegador.

Para compartilhar o painel, consulte [docs/compartilhamento.md](docs/compartilhamento.md). Ter o código no GitHub não cria uma hospedagem automaticamente.

Fonte: Olist / Kaggle, sob CC BY-NC-SA 4.0. [Origem do CSV](docs/origem_da_base.json) · [Histórico de verificações](docs/verificacao.md) · [Registro de assistência](uso_de_ia.md).
