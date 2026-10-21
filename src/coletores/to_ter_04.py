"""Coletor TO-TER-04 (IBGE - Área territorial dos 139 municípios do TO) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER04(ColetorSidra):
    id_fonte = "TO-TER-04"
    id_indicador = "area_territorial"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-04",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = (
        "4714",
        "6318",
        "2022",
    )  # SIDRA 4714: área da unidade territorial (Censo)
    unidade = "km²"
