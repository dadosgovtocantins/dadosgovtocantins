"""
Testes unitários dos 3 coletores do Bloco Saúde DATASUS (Task 14).
"""

from tests.fixtures.saude_payloads import (
    fixture_cnes_leitos,
    fixture_pni_vacinas,
    fixture_sim_mortalidade,
)


def test_to_sau_01_cnes_leitos_139():
    from src.coletores.to_sau_01 import ColetorTOSAU01

    c = ColetorTOSAU01(ambiente="dev")
    registros = c.transformar(fixture_cnes_leitos())
    assert len(registros) == 139
    assert all(r["id_indicador"] == "leitos_sus" for r in registros)


def test_to_sau_02_pni_vacinas_139():
    from src.coletores.to_sau_02 import ColetorTOSAU02

    c = ColetorTOSAU02(ambiente="dev")
    registros = c.transformar(fixture_pni_vacinas())
    assert len(registros) == 139
    assert all(r["unidade"] == "%" for r in registros)


def test_to_sau_03_sim_mortalidade_139():
    from src.coletores.to_sau_03 import ColetorTOSAU03

    c = ColetorTOSAU03(ambiente="dev")
    registros = c.transformar(fixture_sim_mortalidade())
    assert len(registros) == 139
    assert all(r["unidade"] == "óbitos/mil nascidos" for r in registros)


def test_contrato_max_50_linhas_saude():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in ["to_sau_01.py", "to_sau_02.py", "to_sau_03.py"]:
        linhas = (pasta / arq).read_text("utf-8").splitlines()
        assert len(linhas) <= 55, f"{arq} excede limite de linhas ({len(linhas)})"


def test_contrato_nao_sobrescreve_executar_saude():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in ["to_sau_01.py", "to_sau_02.py", "to_sau_03.py"]:
        conteudo = (pasta / arq).read_text("utf-8")
        assert "def executar(" not in conteudo, f"{arq} sobrescreve executar()"
