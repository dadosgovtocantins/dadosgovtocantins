"""Coletor TO-TER-05 (IBGE - PAM: Valor da Produção Agrícola Municipal) <= 50 linhas (RNF-E02)."""

from typing import Any, ClassVar

from src.coletores.sidra import ColetorSidra


class ColetorTOTER05(ColetorSidra):
    id_fonte = "TO-TER-05"
    id_indicador = "producao_agricola"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TER-05",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (checado em 31/08/2026)",
    }
    agregado, variavel, periodos = "5457", "215", "-5"  # SIDRA 5457: valor da produção
    unidade = "R$ mil"
    classificacao = "782[0]"  # 0 = total das lavouras
