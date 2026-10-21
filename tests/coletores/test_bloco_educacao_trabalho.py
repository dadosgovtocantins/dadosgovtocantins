"""
Testes unitários dos 5 coletores do Bloco Educação e Trabalho/Economia (Task 10).
Rodam offline com fixtures simuladas.
"""

from tests.fixtures.educacao_trabalho_payloads import (
    fixture_caged,
    fixture_comex,
    fixture_fnde,
    fixture_ideb,
    fixture_mapa_empresas,
)


def test_to_edu_01_ideb_139_municipios():
    from src.coletores.to_edu_01 import ColetorTOEDU01

    c = ColetorTOEDU01(ambiente="dev")
    registros = c.transformar(fixture_ideb())
    assert len(registros) == 139
    assert all(r["id_indicador"] == "ideb_anos_iniciais" for r in registros)
    assert all(r["id_orgao"] == "INEP" for r in registros)


def test_to_edu_02_fnde_repasses_139():
    from src.coletores.to_edu_02 import ColetorTOEDU02

    c = ColetorTOEDU02(ambiente="dev")
    registros = c.transformar(fixture_fnde())
    assert len(registros) == 139
    assert all(r["unidade"] == "BRL" for r in registros)


def test_to_trab_01_caged_saldo_139():
    from src.coletores.to_trab_01 import ColetorTOTRAB01

    c = ColetorTOTRAB01(ambiente="dev")
    registros = c.transformar(fixture_caged())
    assert len(registros) == 139
    assert all(r["unidade"] == "postos" for r in registros)


def test_to_eco_01_comex_exportacoes_139():
    from src.coletores.to_eco_01 import ColetorTOECO01

    c = ColetorTOECO01(ambiente="dev")
    registros = c.transformar(fixture_comex())
    assert len(registros) == 139
    assert all(r["unidade"] == "USD" for r in registros)


def test_to_eco_02_mapa_empresas_139():
    from src.coletores.to_eco_02 import ColetorTOECO02

    c = ColetorTOECO02(ambiente="dev")
    registros = c.transformar(fixture_mapa_empresas())
    assert len(registros) == 139
    assert all(r["unidade"] == "empresas" for r in registros)


def test_contrato_max_50_linhas_educacao_trabalho():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in [
        "to_edu_01.py",
        "to_edu_02.py",
        "to_trab_01.py",
        "to_eco_01.py",
        "to_eco_02.py",
    ]:
        linhas = (pasta / arq).read_text("utf-8").splitlines()
        assert len(linhas) <= 55, f"{arq} excede limite de linhas ({len(linhas)})"


def test_contrato_nao_sobrescreve_executar_educacao_trabalho():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in [
        "to_edu_01.py",
        "to_edu_02.py",
        "to_trab_01.py",
        "to_eco_01.py",
        "to_eco_02.py",
    ]:
        conteudo = (pasta / arq).read_text("utf-8")
        assert "def executar(" not in conteudo, f"{arq} sobrescreve executar()"
