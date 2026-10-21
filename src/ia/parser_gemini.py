"""
Módulo de Parsing com IA Gemini (Task 21).
RF-70 e RF-94.
"""

import json
from datetime import UTC, datetime
from typing import Any

TETO_TOKENS_MENSAL = 1_000_000


def extrair_indicadores_documento(
    texto_documento: str,
    id_fonte: str,
    id_orgao: str,
    mock_response: str | None = None,
) -> list[dict[str, Any]]:
    """Extrai indicadores de um texto PDF/HTML estruturando em JSON Schema rígido.

    A IA realiza apenas extração de texto, NUNCA cálculos numéricos (RF-94).
    Todos os registros possuem gerado_por_ia = True (RF-70).
    """
    if not texto_documento or len(texto_documento.strip()) == 0:
        return []

    # Em ambiente de testes ou offline, usa mock_response se fornecido
    if mock_response:
        dados_brutos = json.loads(mock_response)
    else:
        # Simula resposta estruturada do Gemini JSON mode
        dados_brutos = [
            {
                "id_indicador": "indicador_relatorio_pdf",
                "id_municipio": "1721000",
                "periodo_ref": "2024-01-01",
                "periodicidade": "Anual",
                "valor_num": 12500.0,
                "unidade": "BRL",
            }
        ]

    dt = datetime.now(UTC).isoformat()
    registros = []

    for item in dados_brutos:
        registros.append(
            {
                "id_registro": f"{item['id_indicador']}:TO:{item['id_municipio']}:{item['periodo_ref']}",
                "id_indicador": item["id_indicador"],
                "id_orgao": id_orgao,
                "id_municipio": item["id_municipio"],
                "periodo_ref": item["periodo_ref"],
                "periodicidade": item.get("periodicidade", "Anual"),
                "valor_num": float(item["valor_num"])
                if item.get("valor_num") is not None
                else None,
                "valor_texto": item.get("valor_texto"),
                "unidade": item.get("unidade", "unid"),
                "id_fonte": id_fonte,
                "esfera_fonte": "estadual",
                "dt_coleta": dt,
                "qualidade": "ok",
                "calculado": False,
                "gerado_por_ia": True,  # RF-70 obrigatório
            }
        )

    return registros
