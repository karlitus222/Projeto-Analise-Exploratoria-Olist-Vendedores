from pathlib import Path

from .funcoes import (
    construir_tabela_analitica,
    limpar_dados,
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

    pasta_tabelas = Path(pasta_saida) / "tabelas_analiticas"
    pasta_tabelas.mkdir(parents=True, exist_ok=True)

    tabela_analitica.to_csv(
        pasta_tabelas / "tabela_vendedor_pedido.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return tabela_analitica
