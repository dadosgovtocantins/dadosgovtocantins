"""
Coletores sem coleta real implementada não podem gerar números (Task 28, RF-55).
Antes, extrair() devolvia valores simulados com códigos IBGE inventados.
"""

import importlib

import pytest
from src.coletor_base.excecoes import ColetaNaoImplementadaError, FonteIndisponivelError

NAO_IMPLEMENTADOS = {
    "to_edu_01": "ColetorTOEDU01",
    "to_edu_02": "ColetorTOEDU02",
    "to_trab_01": "ColetorTOTRAB01",
    "to_eco_01": "ColetorTOECO01",
    "to_eco_02": "ColetorTOECO02",
    "to_sau_01": "ColetorTOSAU01",
    "to_sau_02": "ColetorTOSAU02",
    "to_sau_03": "ColetorTOSAU03",
    "to_rec_01": "ColetorTOREC01",
    "to_rec_03": "ColetorTOREC03",
}


@pytest.mark.parametrize(("modulo", "classe"), NAO_IMPLEMENTADOS.items())
def test_extrair_nao_gera_valores(modulo, classe):
    cls = getattr(importlib.import_module(f"src.coletores.{modulo}"), classe)
    with pytest.raises(ColetaNaoImplementadaError, match="ainda não implementada"):
        cls(ambiente="dev").extrair()


@pytest.mark.parametrize(("modulo", "classe"), NAO_IMPLEMENTADOS.items())
def test_executar_falha_explicitamente_e_nao_grava(modulo, classe, tmp_path, monkeypatch):
    """No ciclo completo (executar) a coleta falha com mensagem clara e nada é gravado na zona raw."""
    monkeypatch.chdir(tmp_path)
    cls = getattr(importlib.import_module(f"src.coletores.{modulo}"), classe)
    coletor = cls(ambiente="dev")
    with pytest.raises(FonteIndisponivelError, match="ainda não implementada"):
        coletor.executar()
    assert not list((tmp_path / ".data_raw").rglob("*.json"))
