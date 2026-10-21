"""
Módulo de validação de dados transformados antes da carga.
PRD v4.2 §1.3 (RF-64, RF-65) e Task 06.
"""

import math
from typing import Any

from src.coletor_base.excecoes import ValidacaoError

CARGOS_TITULAR = frozenset({"PREFEITO", "GOVERNADOR"})


def validar_titulares(registros: list[dict[str, Any]], municipios_validos: set[str]) -> None:
    """
    Valida linhas de dim_titular antes da carga (RF-64, S2 — task 30).
    Prefeito exige id_municipio entre os 139 códigos IBGE canônicos; governador exige NULL.
    No máximo 1 titular por cargo/território e exatamente 1 governador.
    """
    if not registros:
        raise ValidacaoError("Zero titulares gerados na transformação.")
    chaves = [r.get("id_titular") for r in registros]
    if len(set(chaves)) != len(chaves):
        raise ValidacaoError(
            "id_titular duplicado: mais de um titular para o mesmo cargo/território."
        )
    for r in registros:
        cargo, mun = r.get("cargo"), r.get("id_municipio")
        if cargo not in CARGOS_TITULAR:
            raise ValidacaoError(f"Cargo fora do escopo (só titular eleito): {cargo!r}")
        if not str(r.get("nome_titular") or "").strip():
            raise ValidacaoError(f"{r.get('id_titular')}: nome_titular vazio.")
        if cargo == "PREFEITO" and mun not in municipios_validos:
            raise ValidacaoError(f"Município fora dos 139 do TO: {mun!r}")
        if cargo == "GOVERNADOR" and mun is not None:
            raise ValidacaoError("Governador é nível estadual: id_municipio deve ser NULL.")
    if sum(r["cargo"] == "GOVERNADOR" for r in registros) != 1:
        raise ValidacaoError("Esperado exatamente 1 governador do TO.")


def validar_registros(registros: list[dict[str, Any]], cobertura_minima_pct: float = 90.0) -> None:
    """
    Valida a lista de dicionários antes da carga no BigQuery (RF-64).
    Lança ValidacaoError se algum critério falhar.
    """
    if not registros:
        raise ValidacaoError("Zero registros gerados na transformação.")

    municipios_vistos: set[str] = set()

    for idx, r in enumerate(registros):
        # 1. Período de referência obrigatório
        if not r.get("periodo_ref"):
            raise ValidacaoError(f"Registro {idx}: 'periodo_ref' ausente.")

        # 2. Pelo menos um dos valores (numérico ou texto) deve existir
        if r.get("valor_num") is None and not r.get("valor_texto"):
            raise ValidacaoError(
                f"Registro {idx} ({r.get('id_indicador')}): 'valor_num' e 'valor_texto' não podem ser ambos nulos."
            )

        # 3. ID do indicador e da fonte obrigatórios
        if not r.get("id_indicador"):
            raise ValidacaoError(f"Registro {idx}: 'id_indicador' ausente.")
        if not r.get("id_fonte"):
            raise ValidacaoError(f"Registro {idx}: 'id_fonte' ausente.")

        # Rastrear cobertura municipal se houver id_municipio
        id_mun = r.get("id_municipio")
        if id_mun:
            municipios_vistos.add(str(id_mun))

    # 4. Checagem de Cobertura Municipal para dados de nível municipal (139 municípios do TO)
    if municipios_vistos:
        total_mun = len(municipios_vistos)
        pct_cobertura = (total_mun / 139.0) * 100.0
        # Se for um indicador municipal completo, exige cobertura mínima
        if total_mun > 10 and pct_cobertura < cobertura_minima_pct:
            raise ValidacaoError(
                f"Cobertura municipal insuficiente: {total_mun}/139 municípios ({pct_cobertura:.1f}% < {cobertura_minima_pct}%)."
            )


def checar_variacao_3_sigma(valor_novo: float, historico_valores: list[float]) -> str:
    """
    Verifica se o valor_novo excede 3 desvios-padrão (3-sigma) em relação ao histórico.
    Retorna 'ok' ou 'suspeito' (RF-65).
    """
    if len(historico_valores) < 3:
        return "ok"

    media = sum(historico_valores) / len(historico_valores)
    variancia = sum((x - media) ** 2 for x in historico_valores) / len(historico_valores)
    desvio_padrao = math.sqrt(variancia)

    if desvio_padrao == 0:
        return "ok" if valor_novo == media else "suspeito"

    z_score = abs(valor_novo - media) / desvio_padrao
    if z_score > 3.0:
        return "suspeito"

    return "ok"
