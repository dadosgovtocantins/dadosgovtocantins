"""
Testes unitários de indicadores calculados (Task 16).
"""

from src.indicadores.calculador import (
    calcular_densidade_demografica,
    calcular_pib_per_capita,
    gerar_registro_calculado,
)


def test_calcular_pib_per_capita_sucesso():
    # PIB R$ 50.000 mil (R$ 50M) / Pop 10.000 -> 5.000 R$/hab
    res = calcular_pib_per_capita(50_000.0, 10_000)
    assert res == 5000.0


def test_calcular_pib_per_capita_sem_dado():
    res = calcular_pib_per_capita(None, 10_000)
    assert res is None


def test_calcular_densidade_demografica_sucesso():
    # Pop 15.000 / Area 1.500 km² -> 10.0 hab/km²
    res = calcular_densidade_demografica(15_000, 1_500.0)
    assert res == 10.0


def test_gerar_registro_calculado_marca_flags_obrigatorias():
    reg = gerar_registro_calculado(
        id_indicador="pib_per_capita",
        id_municipio="1721000",
        periodo_ref="2024-01-01",
        valor_num=35000.5,
        unidade="R$/hab",
    )
    assert reg["calculado"] is True
    assert reg["gerado_por_ia"] is False
    assert reg["qualidade"] == "ok"


def test_gerar_registro_calculado_sem_dado_preserva_flag():
    reg = gerar_registro_calculado(
        id_indicador="pib_per_capita",
        id_municipio="1721000",
        periodo_ref="2024-01-01",
        valor_num=None,
        unidade="R$/hab",
    )
    assert reg["calculado"] is True
    assert reg["gerado_por_ia"] is False
    assert reg["qualidade"] == "sem_dado"
    assert reg["valor_num"] is None
