# [IA] registro 2 e 16

from pathlib import Path


from .funcoes import (
    codificar_atributos,
    construir_tabela_analitica,
    limpar_dados,
    normalizar_atributos,
    relacionar_tabelas,
)


def preprocessar(
    orders,
    items,
    products,
    sellers,
    reviews,
    pasta_saida=Path.cwd(),
):
    # Coordena a limpeza, os relacionamentos, os cálculos e as exportações.
    dados_brutos = {
        "orders": orders,
        "items": items,
        "products": products,
        "sellers": sellers,
        "reviews": reviews,
    }

    dados_limpos = limpar_dados(dados_brutos)
    base_itens = relacionar_tabelas(dados_limpos)
    tabela_analitica = construir_tabela_analitica(base_itens)
    tabela_analitica = codificar_atributos(tabela_analitica)
    tabela_analitica = normalizar_atributos(tabela_analitica)

    pasta_tabelas = Path(pasta_saida) / "tabelas_analiticas"
    pasta_tabelas.mkdir(parents=True, exist_ok=True)

    tabela_analitica.to_csv(
        pasta_tabelas / "tabela_vendedor_pedido.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return tabela_analitica
