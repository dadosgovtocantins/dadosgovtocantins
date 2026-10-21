"""Coletor TO-TER-02 (IBGE - PIB Municipal dos 139 municípios do TO) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER02(ColetorSidra):
    id_fonte = "TO-TER-02"
    id_indicador = "pib_municipal"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-02",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = "5938", "37", "-5"  # SIDRA 5938: PIB a preços correntes
    unidade = "R$ mil"
