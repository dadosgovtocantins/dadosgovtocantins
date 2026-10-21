"""Histórico longo para o 3σ: busca na API as séries do estado, sem rede (respostas reais gravadas)."""

import pytest
from src.orquestracao.historico import BUSCA_HISTORICA, historico_estadual


@pytest.mark.parametrize(
    ("fonte", "minimo"), [("TO-TER-01", 20), ("TO-TER-03", 15), ("TO-TER-07", 50)]
)
def test_historico_traz_serie_longa_do_estado_em_ordem(rede_gravada, fonte, minimo):
    serie = historico_estadual(fonte)
    assert len(serie) >= minimo
    assert all(isinstance(v, int | float) for _, v in serie)
    assert [r for r, _ in serie] == sorted({r for r, _ in serie}, key=lambda r: (r[-4:], r[:-4]))


def test_historico_pede_a_api_com_periodos_e_localidades_proprios(rede_gravada):
    historico_estadual("TO-TER-07")
    (url,) = rede_gravada
    assert "/periodos/-80/" in url and "localidades=N3[17]" in url


def test_historico_so_existe_para_fontes_com_3_sigma():
    assert set(BUSCA_HISTORICA) == {"TO-TER-01", "TO-TER-03", "TO-TER-07"}
    with pytest.raises(KeyError):
        historico_estadual("TO-TER-05")
