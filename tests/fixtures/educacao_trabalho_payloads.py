"""
Fixtures SINTÉTICAS dos coletores de Educação e Trabalho (Task 10): sem coleta real ainda, só testam o contrato de transformar().
"""

import json


def fixture_ideb() -> bytes:
    """Payload simulado INEP/IDEB (TO-EDU-01)."""
    sim = [
        {
            "id_municipio": f"17{str(i).zfill(5)}",
            "ideb_anos_iniciais": round(4.5 + (i % 25) * 0.1, 1),
        }
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")


def fixture_fnde() -> bytes:
    """Payload simulado FNDE Repasses (TO-EDU-02)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "valor_repassado": 150_000.0 + i * 4_500.0}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")


def fixture_caged() -> bytes:
    """Payload simulado Novo CAGED (TO-TRAB-01)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "saldo_movimentacao": (i * 37) % 500 - 100}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2024-01-01", "resultados": sim}).encode("utf-8")


def fixture_comex() -> bytes:
    """Payload simulado Comex Stat Balança Comercial (TO-ECO-01)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "valor_exportado_usd": (i * 12345) % 1_000_000}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")


def fixture_mapa_empresas() -> bytes:
    """Payload simulado Mapa de Empresas (TO-ECO-02)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "qtd_empresas_ativas": 300 + i * 25}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2024-01-01", "resultados": sim}).encode("utf-8")
