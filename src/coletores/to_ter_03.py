"""Coletor TO-TER-03 (IBGE - PIB Estadual do Tocantins) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER03(ColetorSidra):
    id_fonte = "TO-TER-03"
    id_indicador = "pib_estadual"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-03",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = "5938", "37", "-5"  # SIDRA 5938: PIB a preços correntes
    unidade = "R$ mil"
    localidades = "N3[17]"
