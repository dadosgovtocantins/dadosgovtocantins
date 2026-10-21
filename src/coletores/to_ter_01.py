"""Coletor TO-TER-01 (IBGE - População 139 municípios TO) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER01(ColetorSidra):
    id_fonte = "TO-TER-01"
    id_indicador = "populacao_residente"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }
    agregado, variavel, periodos = "6579", "9324", "-3"  # SIDRA 6579: população residente estimada
    unidade = "hab"
