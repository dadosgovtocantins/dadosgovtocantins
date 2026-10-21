"""
Módulo de cálculo de indicadores derivados (Task 16).
Garante que todo registro calculado possua calculado = True e gerado_por_ia = False.
"""

from typing import Any


def calcular_pib_per_capita(pib_mil_reais: float | None, populacao: float | None) -> float | None:
    """Calcula o PIB per capita em R$/hab."""
    if pib_mil_reais is None or populacao is None or populacao <= 0:
        return None
    return round((pib_mil_reais * 1000.0) / populacao, 2)


def calcular_densidade_demografica(populacao: float | None, area_km2: float | None) -> float | None:
    """Calcula a densidade demográfica em hab/km²."""
    if populacao is None or area_km2 is None or area_km2 <= 0:
        return None
    return round(populacao / area_km2, 2)


def gerar_registro_calculado(
    id_indicador: str,
    id_municipio: str,
    periodo_ref: str,
    valor_num: float | None,
    unidade: str,
) -> dict[str, Any]:
    """Gera o dicionário de registro formatado conforme o esquema canônico da fato."""
    is_sem_dado = valor_num is None
    return {
        "id_registro": f"{id_indicador}:TO:{id_municipio}:{periodo_ref}",
        "id_indicador": id_indicador,
        "id_municipio": id_municipio,
        "periodo_ref": periodo_ref,
        "valor_num": valor_num,
        "unidade": unidade,
        "calculado": True,
        "gerado_por_ia": False,
        "qualidade": "sem_dado" if is_sem_dado else "ok",
    }
