"""Coletor TO-TER-07 (IBGE - PNADC: taxa de desocupação do TO) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER07(ColetorSidra):
    id_fonte = "TO-TER-07"
    id_indicador = "taxa_desocupacao"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-07",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = (
        "4099",
        "4099",
        "-4",
    )  # SIDRA 4099: taxa de desocupação trimestral
    unidade = "%"
    localidades = "N3[17]"  # PNADC é estadual
    periodicidade = "Trimestral"
