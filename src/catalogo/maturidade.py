"""
Módulo de cálculo do Índice de Maturidade de Dados Abertos (Task 19).
RF-43 e RF-44.
"""

from typing import Any

ORGAOS_CATALOGADOS = [
    "IBGE",
    "INEP",
    "FNDE",
    "MTE",
    "MDIC",
    "ME",
    "DATASUS",
    "STN",
    "SEFAZ-TO",
    "SES-TO",
    "SEDUC-TO",
    "TCE-TO",
    "SEAGRO-TO",
    "CGE-TO",
]


def calcular_pontuacao_maturidade(fontes: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula a maturidade de dados abertos para um conjunto de fontes."""
    total = len(fontes)
    if total == 0:
        return {
            "total_fontes": 0,
            "reutilizaveis_ab": 0,
            "apenas_link_d": 0,
            "percentual_reuso": 0.0,
            "nivel": "Inexistente",
        }

    reutilizaveis = sum(1 for f in fontes if f.get("classe_reuso") in ["A", "B"])
    apenas_link = total - reutilizaveis
    pct = round((reutilizaveis / total) * 100.0, 1)

    if pct >= 80.0:
        nivel = "Avançado"
    elif pct >= 50.0:
        nivel = "Intermediário"
    elif pct > 0.0:
        nivel = "Inicial"
    else:
        nivel = "Inexistente"

    return {
        "total_fontes": total,
        "reutilizaveis_ab": reutilizaveis,
        "apenas_link_d": apenas_link,
        "percentual_reuso": pct,
        "nivel": nivel,
    }


def avaliar_maturidade_orgaos() -> dict[str, dict[str, Any]]:
    """Mapeia os 14 órgãos e calcula a maturidade de cada um."""
    # Matriz sintética baseada no catálogo de 18 fontes + fontes estaduais apenas-link
    mapa_fontes = {
        "IBGE": [
            {"classe_reuso": "A"},
            {"classe_reuso": "A"},
            {"classe_reuso": "A"},
            {"classe_reuso": "A"},
        ],
        "INEP": [{"classe_reuso": "A"}],
        "FNDE": [{"classe_reuso": "A"}],
        "MTE": [{"classe_reuso": "A"}],
        "MDIC": [{"classe_reuso": "A"}],
        "ME": [{"classe_reuso": "A"}],
        "DATASUS": [{"classe_reuso": "A"}, {"classe_reuso": "A"}, {"classe_reuso": "A"}],
        "STN": [{"classe_reuso": "A"}, {"classe_reuso": "A"}, {"classe_reuso": "A"}],
        "SEFAZ-TO": [{"classe_reuso": "D"}],  # Gate 1: Vaadin sem API
        "SES-TO": [{"classe_reuso": "D"}],
        "SEDUC-TO": [{"classe_reuso": "D"}],
        "TCE-TO": [{"classe_reuso": "D"}],  # Gate 1: Portal do Cidadão TCE-TO
        "SEAGRO-TO": [{"classe_reuso": "D"}],  # Gate 1: Lab63 Gov TO
        "CGE-TO": [{"classe_reuso": "D"}],  # Gate 1: SIAFE / Transparência TO
    }

    return {
        orgao: calcular_pontuacao_maturidade(mapa_fontes.get(orgao, []))
        for orgao in ORGAOS_CATALOGADOS
    }
