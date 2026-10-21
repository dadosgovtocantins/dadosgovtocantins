"""
Fixtures dos coletores de Recursos Financeiros. TO-REC-02 usa resposta REAL gravada (Task 28).
TO-REC-01 e TO-REC-03 ainda não têm coleta real: seus payloads são SINTÉTICOS e só testam o contrato de transformar().
"""

import json
from pathlib import Path


def fixture_transferegov() -> bytes:
    """Payload simulado Transferegov Convênios (TO-REC-01)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "valor_convenios_brl": 500_000.0 + (i * 25_000.0)}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")


def fixture_siconfi_rcl() -> bytes:
    """Recorte REAL do SICONFI (RREO Anexo 3, RCL anual) gravado em 2026-10-14: estado, Palmas e Araguaína, 2024 e 2025.

    Mesmo formato que coletar_rcl() grava na zona raw (TO-REC-02).
    """
    return (Path(__file__).parent / "gravadas" / "siconfi_rcl_recorte.json").read_bytes()


def fixture_siconfi_rgf() -> bytes:
    """Recorte REAL do SICONFI (RGF Simplificado Anexo 1, RCL), gravado em 2026-10-14: Abreulândia, 2024 e 2025.

    Abreulândia entrega o RREO Simplificado (sem Anexo 3), então sua RCL só existe no RGF.
    """
    return (Path(__file__).parent / "gravadas" / "siconfi_rgf_recorte.json").read_bytes()


def fixture_capag() -> bytes:
    """Payload simulado CAPAG Tesouro Nacional (TO-REC-03)."""
    niveis = ["A", "B", "C"]
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "capag_nota": niveis[i % 3]} for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")
