# Verificação da etapa 7

## Filtros persistentes, interatividade e recorte PI - 27/11/2026

- UF fixa em PI aplicada antes dos demais filtros. O CSV completo não foi alterado.
- Recorte real: 12 pedidos, um vendedor, 11 despachos elegíveis e 11 avaliações elegíveis.
  Não há despachos atrasados entre os elegíveis; nota média 4,00. Não existe comparação entre vários vendedores ou entre os dois grupos de atraso neste estado.
- Nome fictício de exibição: Loja Aurora. ID original `47efca563408aae19bb7206c2d969ea9` preservado.
- Ano e UF no topo; mês, vendedor e período em seção recolhível. Ano, mês, vendedor e período permanecem selecionados ao navegar entre páginas.
  A causa da perda anterior foi a limpeza das chaves de widgets ao trocar de página no Streamlit. Chaves permanentes separadas corrigiram esse comportamento.
- Gráficos Altair 5.5.0 com tooltips, zoom e arraste; gráficos de barras e dispersão também têm seleção por clique para destacar dados.
  O destaque e o zoom são visuais; os indicadores são determinados pelos filtros.
- O gráfico de despacho inclui um ponto sobre a barra, para permitir visualizar e consultar o valor real de 0%.
- Sínteses descritivas calculadas para os dados filtrados do PI. Respostas nacionais recebidas da equipe preservadas em referência separada.
- Teste inicial demonstrou que o painel ainda exibia 98.666 pedidos, em vez dos 12 do PI. Após as alterações: **9 passed in 6.55s**.
  Os testes cobrem páginas, escopo PI, nomes fictícios e IDs, persistência entre páginas, período incompleto/vazio, controles do cenário e especificações interativas dos gráficos.
- Compilação sem erros. Inspeção visual confirmou os filtros no celular, os dados reais do PI e a renderização dos gráficos no computador, sem erros no console observado.
- Após usar a opção `width='stretch'` compatível com o Streamlit instalado, nova execução: **9 passed in 7.03s**; `pip check`: `No broken requirements found`.
- Nenhum commit, push ou alteração no repositório compartilhado. O link Cloudflare anterior expirou e não havia processo de túnel ativo nesta revisão.
  O compartilhamento externo exige novo início manual pelo proprietário, conforme `compartilhamento.md`.

Referências oficiais consultadas com Context7: widgets multipágina do Streamlit e seleções/zoom do Altair.
Não foi usada a API nova `persist_state`, ausente no Streamlit 1.51.0; foi aplicado o padrão de chaves temporárias e permanentes compatível com essa versão.

As seções abaixo preservam o histórico das versões nacionais anteriores. As suas contagens não representam o recorte PI atual.

## Revisão dos quatro requisitos - 26/11/2026

- Uma página para cada pergunta: três módulos em `pages/` e visão geral em `app.py`.
- Filtros de estado, vendedor e período presentes e testados.
- Seção “Conclusão de negócio” em cada página. As respostas recebidas foram preservadas sem atribuir novos textos à equipe.
  A legenda informa que os textos se referem à base completa, enquanto tabelas, gráficos e indicadores acompanham o recorte.
- Números do painel lidos somente de `data/processed/tabela_analitica.csv`.
  O JSON de conclusões contém os textos, sem ser usado como fonte dos cálculos.
- Onze arquivos compartilhados, incluindo base, páginas e cálculos, conferidos novamente com o commit `f56b0fe` do GitHub.
- `python -m pytest -q`: **7 passed in 52.21s**. A suíte agora também confere título, texto da conclusão e controles em cada página.
- Nenhum commit ou push realizado. A tentativa de criar túnel externo foi bloqueada pela revisão automática de aprovação.
  Nenhum túnel foi iniciado por essa tentativa. O solicitante preferiu um link temporário sem Render; nenhuma hospedagem Render foi criada.
- A revisão exata foi iniciada em novo processo local na porta 8503, evitando a sessão antiga da porta 8502.
  A seção “Conclusão de negócio” foi observada no navegador. A visão geral foi conferida nas dimensões 390x844 e 1280x800.
  O acesso externo da cópia revisada ainda depende do início manual do túnel e da conferência do endereço gerado.

## Histórico da organização - 25/11/2026

Pasta local: `streamlit`. Responsável informado: Guilherme Estrela.

## Referência do grupo

- Repositório: https://github.com/guilhermeestrela10/projeto-analise-exploratoria-ciencia-de-dados
- Commit consultado: `f56b0fe1a0e2447b6004da932e133388b680d1fe`, de 24/11/2026.
- O commit alterou README, links e registros de documentação. Código analítico e dados permaneceram iguais.
- A referência remota foi consultada novamente ao concluir os testes e continuava nesse commit.
- Nenhum commit, push ou deploy foi feito nesta entrega. A cópia local original do projeto permaneceu limpa.

## Compatibilidade dos arquivos

Onze arquivos compartilhados foram comparados com seus objetos Git no commit remoto:
entrada, três páginas, módulos de análise, gráficos e carga, configuração visual, tabela e resumos recebidos.
Todos coincidem com a referência. As assinaturas estão em `origem_da_base.json`.

Tabela final preservada:

- 100.010 linhas, 41 colunas e 98.666 pedidos distintos.
- Chave pedido-vendedor sem duplicações.
- 94.955 despachos elegíveis; 94.257 pedidos elegíveis com nota.
- 38.273.457 bytes; SHA256 `dfad55639d8981825300bce364f6faf7a7e1ee45efda0d696ce859a73b7d958c`.

O JSON de origem descreve os bytes efetivamente incluídos nesta pasta, com finais de linha LF.
O arquivo histórico `metadados.json` do repositório não é necessário para executar o painel e não foi duplicado.

## Alterações apenas nesta cópia

- Organização da etapa 7 em uma pasta independente, com documentação curta em `docs/`.
- Filtros com os textos “Todos os estados” e “Todos os vendedores”.
- Datas apresentadas como dia/mês/ano.
- Mantidos os ajustes locais anteriores: escopo dos resumos da base completa e distinção entre simulador e critérios fixos.
- Dependências restritas ao painel e aos testes; diretórios temporários e logs fora do ZIP.

Nenhuma alteração nas métricas, critérios, denominadores ou regras do processamento do grupo.

## Testes executados

Na raiz desta pasta, com Python 3.11 do ambiente já instalado do projeto:

```text
python -m pytest -q
7 passed in 107.26s (0:01:47)
```

Cobertura dos testes:

- Abertura da visão geral e das três páginas.
- Filtro de UF e tratamento de recorte vazio.
- Período incompleto e período de um dia.
- Filtro por vendedor válido com conferência dos pedidos e dos grupos de avaliações.
- Simulador nos limiares 0% e 100%, volume mínimo de 10.000 e preservação dos indicadores gerais.

`compileall -q src pages app.py tests`: sem erros.
`pip check` no ambiente usado: `No broken requirements found`.

O painel desta pasta foi iniciado localmente em http://127.0.0.1:8502/.
O endpoint de saúde retornou `ok`; a visão geral foi conferida visualmente com indicadores,
filtros em português e período `04/09/2016 - 03/09/2018`.
As três páginas foram verificadas por AppTest; a inspeção visual manual desta sessão se limitou à visão geral.
O painel público anterior não foi atualizado nesta entrega.

Se o grupo publicar alterações futuras nas tabelas ou regras, conferir novamente a integração.

## Referências técnicas consultadas com Context7

- https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
- https://docs.streamlit.io/develop/api-reference/widgets/st.date_input

Assistência registrada na linha 10 de `uso_de_ia.md`.


## Correção dos filtros — 27/11/2026

Ano e mês agora ajustam automaticamente o período; o usuário pode refinar os dias depois. Junho está disponível e informa ausência de pedidos no recorte PI. A visão geral passou a exibir o gráfico mensal interativo. Teste de regressão reproduziu o calendário antigo e a ausência do gráfico antes da correção. Validação final: 10 testes passaram em 13,27 s. No link público, fevereiro ajustou o calendário para 01/02/2018–28/02/2018, os indicadores para 5 pedidos e o gráfico para 2018-02. CSV e GitHub não foram alterados.


## Revisão de todas as páginas e filtros — 27/11/2026

A visão geral contém gráfico mensal e tabela interativa. As três páginas de análise contêm tabelas e gráficos interativos, incluindo o gráfico de nota e atraso na janela de acompanhamento. A referência nacional fixa saiu da interface e permanece no arquivo original para evitar confusão com os dados filtrados. Os testes conferem janeiro a agosto em todas as páginas, números dos indicadores, dados Arrow enviados aos gráficos e totais das tabelas contra o CSV. Também verificam troca de página, calendário, junho sem pedidos e 05/01/2018 com pedido não elegível: nesses casos há explicação no lugar de gráficos vazios. Nenhuma alteração no CSV ou GitHub.

Validação final: 18 testes passaram em 15,61 s. Conferência no navegador público: gráfico de critérios, gráficos de avaliações, gráfico e tabela da visão geral; layout em 390 × 844 e nenhum erro de console observado. Julho conferido com período 01/07/2018–31/07/2018 e 1 pedido.


## Ano completo e doze meses — 27/11/2026

Todas as abas oferecem janeiro a dezembro. Trocar o ano restaura todos os meses e o calendário de 01/01 a 31/12. O calendário permite meses sem registros. Nesses recortes, os indicadores mostram 0 pedidos, 0 despachos elegíveis e 0 avaliações; a taxa fica Sem dados. Há tabela vazia e conclusão explicativa. A base PI possui 12 pedidos, todos de 2018; junho e setembro a dezembro não possuem registros. Não foram criadas linhas sintéticas. Validação: 22 testes passaram em 21,70 s, cobrindo os 12 meses nas quatro páginas. No navegador público, dezembro mostrou 0 pedidos e selecionar 2018 restaurou os 12 pedidos anuais. CSV e GitHub preservados.


## Entrega no repositório dos colaboradores — 27/11/2026

Versão demonstrada copiada para streamlit/ no repositório karlitus222/Projeto-Analise-Exploratoria-Olist-Vendedores, sobre o commit 05a8c34bea04c90eabd355f5956a76efea3f35b0. Nenhum arquivo anterior do grupo foi alterado. Os 22 testes passaram nesta cópia em 21,18 s. O SHA256 do CSV foi conferido com docs/origem_da_base.json. O painel mantém seu CSV de 41 colunas; o CSV de 46 colunas do pipeline dos colaboradores exige adaptação de contrato, descrita em docs/continuar_desenvolvimento.md. Código da aplicação e dados preservam a última versão demonstrada.
