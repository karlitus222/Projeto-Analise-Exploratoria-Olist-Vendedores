"""Labels e conclusões de negócio alinhadas à etapa 6 do notebook."""
# [IA] registro 15
from .analysis import delay_ranking

ORIGINAL_CONCLUSIONS = {
    "atrasos": (
        "Na análise original, 811 vendedores tinham pelo menos 20 despachos "
        "avaliáveis. As maiores taxas foram: ID 48efc9d9 (PR; 28 de 33; "
        "84,85%), ID 835f0f78 (SP; 31 de 42; 73,81%) e ID a7f13822 "
        "(SP; 45 de 75; 60,00%). "
        "O ranking destaca os maiores percentuais observados; não significa "
        "que essa proporção de vendedores concentre todos os problemas."
    ),
    "avaliacoes": (
        "Sim, os pedidos avaliados com atraso tiveram notas piores na análise "
        "original: média 3,67 contra 4,16 nos pedidos sem atraso. A proporção "
        "de notas médias de 1 ou 2 foi 24,50% contra 12,80%. A diferença "
        "indica associação, mas não prova que o atraso causou a nota baixa."
    ),
    "criterios": (
        "Na análise original, 811 vendedores atingiram os mínimos definidos: "
        "20 despachos avaliáveis e 10 pedidos com nota. Desses, 591 ficaram "
        "em acompanhamento regular, 172 em advertência e 48 em revisão "
        "prioritária. Os limites são propostas para orientar a análise, não "
        "uma decisão automática sobre o vendedor."
    ),
}


def seller_label(row):
    city = str(row.get("seller_city", "")).strip()
    state = str(row.get("seller_state", "")).strip()
    seller_id = str(row.get("seller_id", ""))
    location = ", ".join(part for part in (city.title(), state) if part)
    if location:
        return f"{location} · {seller_id[:8]}"
    return seller_id


def business_summary(page, data, metrics, comparison, monitored):
    if data.empty:
        return (
            "Não há pedidos neste recorte. Ajuste os filtros para consultar "
            "outros estados, categorias ou períodos."
        )

    if page == "atrasos":
        ranked = delay_ranking(metrics)
        if ranked.empty:
            return (
                "Nenhum vendedor atingiu 20 despachos avaliáveis no recorte. "
                "Não há volume suficiente para formar um ranking confiável."
            )
        leaders = ranked.head(3)
        details = "; ".join(
            f"{seller_label(row)}: {int(row['pedidos_com_atraso_despacho'])} "
            f"de {int(row['pedidos_despacho_avaliavel'])} pedidos "
            f"({row['taxa_atraso_despacho_pct']:.1f}%)"
            for _, row in leaders.iterrows()
        )
        return f"Maiores taxas de atraso no recorte: {details}."

    if page == "avaliacoes":
        available = comparison.dropna(subset=["nota_media"])
        if available.empty:
            return "Não há pedidos com avaliação e situação de despacho conhecida."
        if len(available) < 2:
            group = available.iloc[0]["situacao"]
            return (
                f"Há dados somente para o grupo “{group}”. Sem o grupo oposto, "
                "não é possível comparar notas neste recorte."
            )
        late = available.set_index("situacao").loc["Com atraso no despacho"]
        on_time = available.set_index("situacao").loc["Sem atraso no despacho"]
        direction = (
            "menor"
            if late["nota_media"] < on_time["nota_media"]
            else "maior ou igual"
        )
        return (
            f"Neste recorte, a nota média dos pedidos com atraso é "
            f"{late['nota_media']:.2f}, {direction} à dos pedidos sem atraso "
            f"({on_time['nota_media']:.2f}). Notas 1 ou 2 representam "
            f"{late['taxa_nota_baixa_pct']:.1f}% no grupo com atraso e "
            f"{on_time['taxa_nota_baixa_pct']:.1f}% no grupo sem atraso. "
            "A comparação é descritiva e não comprova causalidade."
        )

    if page == "criterios":
        if monitored.empty:
            return (
                "Nenhum vendedor atingiu simultaneamente os mínimos de "
                "20 despachos avaliáveis e 10 pedidos com nota."
            )
        counts = monitored["classificacao"].value_counts()
        regular = int(counts.get("Acompanhamento regular", 0))
        warning = int(counts.get("Advertência", 0))
        priority = int(counts.get("Revisão prioritária", 0))
        return (
            f"Entre {len(monitored)} vendedores com dados suficientes, "
            f"{regular} ficam em acompanhamento regular, {warning} atingem "
            "ao menos um limite de atenção e "
            f"{priority} atingem os dois. Use os critérios como sinal para "
            "revisão dos registros, não como punição automática."
        )

    return (
        f"O recorte contém {data['order_id'].nunique():,} pedidos e "
        f"{metrics['seller_id'].nunique():,} vendedores. Consulte as três "
        "páginas para comparar os mesmos indicadores da etapa 6."
    )
