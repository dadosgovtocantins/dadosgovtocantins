"""
Testes do cálculo do Índice de Maturidade de Dados Abertos (Task 19).
"""

from src.catalogo.maturidade import (
    ORGAOS_CATALOGADOS,
    avaliar_maturidade_orgaos,
    calcular_pontuacao_maturidade,
)


def test_calcular_pontuacao_maturidade_avancado():
    fontes = [{"classe_reuso": "A"}, {"classe_reuso": "B"}, {"classe_reuso": "A"}]
    res = calcular_pontuacao_maturidade(fontes)
    assert res["total_fontes"] == 3
    assert res["percentual_reuso"] == 100.0
    assert res["nivel"] == "Avançado"


def test_calcular_pontuacao_maturidade_inexistente():
    fontes = [{"classe_reuso": "D"}]
    res = calcular_pontuacao_maturidade(fontes)
    assert res["total_fontes"] == 1
    assert res["percentual_reuso"] == 0.0
    assert res["nivel"] == "Inexistente"


def test_avaliar_maturidade_14_orgaos():
    res = avaliar_maturidade_orgaos()
    assert len(res) == 14
    for o in ORGAOS_CATALOGADOS:
        assert o in res
        assert "nivel" in res[o]
        assert "percentual_reuso" in res[o]
