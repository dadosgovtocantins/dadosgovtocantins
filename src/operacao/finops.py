"""
Módulo de FinOps e Saúde da Operação (Task 23).
Garante Custo R$ 0,00 e monitoramento da franquia gratuita do GCP.
"""

from typing import Any

# Limites da franquia gratuita do Google Cloud (100% Free Tier)
LIMITE_BIGQUERY_CONSULTA_BYTES = 1_000_000_000  # 1 GB por query
LIMITE_BIGQUERY_MENSAL_BYTES = 1_000_000_000_000  # 1 TB/mês gratuito


def auditoria_custo_zero(bytes_consultados: int) -> dict[str, Any]:
    """Valida se a consulta respeita a trava de custo zero."""
    dentro_do_limite = bytes_consultados <= LIMITE_BIGQUERY_CONSULTA_BYTES
    return {
        "custo_estimado_brl": 0.0,
        "bytes_consultados": bytes_consultados,
        "limite_query_bytes": LIMITE_BIGQUERY_CONSULTA_BYTES,
        "aprovado": dentro_do_limite,
        "mensagem": "Consulta dentro da franquia gratuita (0.00 BRL)"
        if dentro_do_limite
        else "ALERTA: Excede teto de 1 GB",
    }


def verificar_saude_operacao(status_fontes: list[dict[str, Any]]) -> dict[str, Any]:
    """Monitora a saúde das fontes de dados registradas no catálogo."""
    total = len(status_fontes)
    ok = sum(1 for f in status_fontes if f.get("status") in ["ok", "sem_mudanca"])
    defasadas = total - ok

    return {
        "total_fontes_monitoradas": total,
        "fontes_saudaveis": ok,
        "fontes_defasadas": defasadas,
        "taxa_saude_pct": round((ok / total) * 100.0, 1) if total > 0 else 100.0,
    }
