"""Coletor TO-TER-06 (IBGE - PPM: Efetivo de bovinos) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER06(ColetorSidra):
    id_fonte = "TO-TER-06"
    id_indicador = "rebanho_bovino"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-06",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = "3939", "105", "-5"  # SIDRA 3939: efetivo dos rebanhos
    unidade = "cabeças"
    classificacao = "79[2670]"  # 2670 = bovino
