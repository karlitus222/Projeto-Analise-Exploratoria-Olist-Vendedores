# Streamlit - Gestão de vendedores parceiros

Etapa 7 de Guilherme Estrela. Grupo 04, Briefing 5.

Painel organizado em uma pasta própria, com a base final necessária para executar a versão atual.
Esta entrega está isolada na pasta streamlit do repositório dos colaboradores. Os arquivos das outras etapas foram preservados. Esta pasta não contém o pipeline, o notebook ou o relatório da etapa 8.

## Abrir no VS Code

Abrir esta pasta `streamlit`. Usar Python 3.11 e executar no terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir o endereço exibido no terminal. Normalmente é http://localhost:8501; se a porta estiver ocupada, usar a porta indicada pelo Streamlit.
Para encerrar, pressionar `Ctrl+C` no terminal. Não executar `app.py` pelo botão comum do Python.

## O que o painel mostra

Os quatro requisitos da entrega foram conferidos em 27/11/2026:

| Requisito | Onde está atendido |
|---|---|
| Uma página para cada pergunta | Três arquivos em `pages/`, além da visão geral |
| Pelo menos dois filtros | Ano, mês, vendedor e período. UF fixa em PI por solicitação do responsável |
| Conclusão em linguagem de negócio por página | Síntese descritiva calculada para os filtros atuais |
| Dados vindos do CSV final do repositório | `data/processed/tabela_analitica.csv`, conferido contra o commit `f56b0fe` |

- **Visão geral:** pedidos distintos, despachos elegíveis, taxa de atraso e pedidos com nota.
- **Atrasos no despacho:** ranking por vendedor, volume mínimo e evolução mensal.
- **Atrasos e avaliações:** notas com e sem atraso, comparação entre vendedores e recorte por atraso ao cliente.
- **Critérios de acompanhamento:** TAD acima de 10%, nota abaixo de 3,8, tempo médio em dias úteis e simulador.

Atualização de 27/11/2026: a análise usa somente vendedores do PI. A base contém **12 pedidos, um vendedor, 11 despachos elegíveis e 11 avaliações elegíveis** nesse estado.
Não há atrasos de despacho entre os pedidos elegíveis do PI. Não é possível comparar grupos com e sem atraso nesse recorte.

Ano e estado ficam no topo; a UF apresenta apenas PI e não pode ser alterada.
O bloco “Mais filtros: mês, período e vendedor” reúne os controles adicionais. As seleções são aplicadas em conjunto e permanecem ao trocar de página.
As sínteses descritivas acompanham os filtros. As respostas nacionais originais foram preservadas em reports/conclusoes_equipe.json como referência documental, sem aparecer na interface.
As datas aparecem como dia/mês/ano. Somente 2018 aparece como ano selecionável, porque os pedidos do PI estão nesse ano.

O vendedor é exibido como **Loja Aurora**, um nome fictício para demonstração. Seu ID original é mantido no CSV, nas tabelas e nos detalhes dos gráficos.
Não foram inventados vendedores nem pedidos adicionais. O recorte atual não permite um ranking entre vários parceiros.
O volume mínimo da página de atrasos limita somente o ranking.
O simulador altera o cenário exibido, sem modificar os critérios fixos ou emitir advertências.
O botão de download exporta o recorte atual em CSV.

Os gráficos usam Altair: detalhes ao passar o cursor ou tocar, destaque por clique, zoom e arraste. Dois cliques restauram a escala.
O zoom altera apenas a visualização; os filtros do topo determinam os indicadores.
O gráfico de vendedores mostra também um ponto para que o valor de 0% continue visível e tenha detalhes acessíveis.

## Pastas

```text
streamlit/
  app.py                         Entrada do painel
  pages/                         Três páginas de análise
  src/                           Interface, métricas e gráficos compartilhados
  data/processed/                Tabela analítica atual
  reports/conclusoes_equipe.json Resumos nacionais de referência
  docs/                          Origem da base e verificações desta cópia
  tests/                         Testes do painel e dos filtros
  .streamlit/config.toml         Tema e navegação
  requirements.txt              Dependências com versões fixas
  uso_de_ia.md                   Registro da assistência
```

`src/load_data.py` foi mantido porque fornece a referência à pasta do projeto usada pelo painel.
Os módulos compartilhados e a base são dependências da integração; sua presença não reatribui as etapas anteriores a Guilherme.

## Compatibilidade com o repositório

Referência consultada em **25/11/2026**: commit `f56b0fe1a0e2447b6004da932e133388b680d1fe`, publicado em 24/11/2026.
Esse commit atualizou documentação e links. Os dados, os cálculos e as páginas permaneceram iguais à referência anterior.
Os links desta entrega usam o nome atual em minúsculas:
https://github.com/guilhermeestrela10/projeto-analise-exploratoria-ciencia-de-dados

A tabela mantém uma linha por pedido-vendedor, 100.010 linhas e 41 colunas.
O arquivo completo permanece intacto; a restrição ao PI é aplicada apenas na interface.
As regras de elegibilidade, avaliação única e métricas foram preservadas.
As respostas originais da base nacional permanecem em reports/conclusoes_equipe.json como referência documental; a interface mostra apenas conclusões do recorte filtrado.
As sínteses descritivas principais usam os dados do recorte PI e acompanham os filtros.
A janela de 30 dias termina na última compra do recorte histórico, não na data atual.
Dias úteis contam segunda a sexta, sem feriados. Não foi definido limite automático para o tempo médio.
A data de despacho pertence ao pedido inteiro; associação entre atraso e nota não demonstra causalidade.

Se o grupo publicar outra base, conferir os nomes, tipos, granularidade e regras antes de substituí-la.
Se os resultados mudarem, revisar também os resumos em `reports/conclusoes_equipe.json`.

## Conferir os testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes usam a tabela incluída e não precisam dos CSVs brutos.
As evidências desta versão ficam em [docs/verificacao.md](docs/verificacao.md).
O commit e as assinaturas dos arquivos de referência ficam em [docs/origem_da_base.json](docs/origem_da_base.json).

## Mostrar aos colegas

A revisão local de 27/11 está aberta em http://127.0.0.1:8503/ neste computador.
Para acesso pelo celular ou computador de outra pessoa, seguir [docs/compartilhamento.md](docs/compartilhamento.md).
O link temporário não faz push no GitHub e exige que o computador e o túnel permaneçam ligados.
Links temporários só funcionam enquanto o computador e o túnel estiverem ativos. Para gerar um novo endereço, seguir as instruções de compartilhamento.


### Filtros de ano e mês

Selecionar o ano restaura Todos os meses e o intervalo de 01/01 a 31/12. Os doze meses estão disponíveis em todas as páginas. Meses sem registros exibem 0 pedidos, tabela vazia e explicação; médias e taxas ficam sem dados. Todos os anos e 2018 têm o mesmo total de 12 pedidos no PI, pois é o único ano observado. Junho e setembro a dezembro não têm pedidos nesta base.


## Continuar o trabalho em equipe

Esta é a versão demonstrada em 27/11/2026, publicada em uma pasta independente. As instruções para executar a partir da raiz do repositório, alterar o painel e integrar o CSV do pipeline dos colegas estão em [docs/continuar_desenvolvimento.md](docs/continuar_desenvolvimento.md).
