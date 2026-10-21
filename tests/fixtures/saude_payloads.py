"""
Fixtures SINTÉTICAS dos coletores de Saúde (Task 14): sem coleta real ainda, só testam o contrato de transformar().
"""

import json


def fixture_cnes_leitos() -> bytes:
    """Payload simulado CNES Leitos SUS (TO-SAU-01)."""
    sim = [
        {"id_municipio": f"17{str(i).zfill(5)}", "leitos_sus": 10 + (i * 3) % 150}
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2024-01-01", "resultados": sim}).encode("utf-8")


def fixture_pni_vacinas() -> bytes:
    """Payload simulado PNI Cobertura Vacinal (TO-SAU-02)."""
    sim = [
        {
            "id_municipio": f"17{str(i).zfill(5)}",
            "cobertura_vacinal_pct": round(70.0 + (i % 28) * 0.9, 1),
        }
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")


def fixture_sim_mortalidade() -> bytes:
    """Payload simulado SIM/SINASC Mortalidade Infantil (TO-SAU-03)."""
    sim = [
        {
            "id_municipio": f"17{str(i).zfill(5)}",
            "taxa_mortalidade_infantil": round(8.0 + (i % 12) * 0.5, 1),
        }
        for i in range(1, 140)
    ]
    return json.dumps({"periodo": "2023", "resultados": sim}).encode("utf-8")
