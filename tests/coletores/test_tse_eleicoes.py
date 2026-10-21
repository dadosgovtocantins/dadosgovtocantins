"""
TSE: a eleição vigente de cada cargo vem da DATA (Task 35, passo 5), não de um ano escrito no código.
Prefeitos: eleições 2024, 2028... Governadores: 2022, 2026... Posse sempre em 1º de janeiro do ano seguinte.
"""

import io
import zipfile
from datetime import date

import pytest
from src.coletores import tse_candidatos
from src.coletores.tse_candidatos import baixar_titulares, eleicoes_vigentes, proxima_posse

HOJE_REAL = tse_candidatos.hoje  # guardado antes do fixture autouse que congela a data (conftest)


@pytest.mark.parametrize(
    ("dia", "prefeito", "governador"),
    [
        (date(2024, 12, 31), 2020, 2022),  # o eleito de 2024 só assume em 1/1/2025
        (date(2025, 1, 1), 2024, 2022),
        (date(2026, 10, 21), 2024, 2022),  # hoje: a eleição de 2026 ainda não deu posse
        (date(2026, 12, 31), 2024, 2022),
        (date(2027, 1, 1), 2024, 2026),  # virada do governador
        (date(2028, 12, 31), 2024, 2026),
        (date(2029, 1, 1), 2028, 2026),  # virada dos prefeitos
        (date(2030, 12, 31), 2028, 2026),
        (date(2031, 1, 1), 2028, 2030),
        (date(2033, 1, 1), 2032, 2030),
    ],
)
def test_eleicao_vigente_pela_data(dia, prefeito, governador):
    assert eleicoes_vigentes(dia) == {"PREFEITO": prefeito, "GOVERNADOR": governador}


@pytest.mark.parametrize(
    ("dia", "posse"),
    [
        (date(2025, 6, 1), date(2027, 1, 1)),
        (date(2026, 10, 21), date(2027, 1, 1)),
        (date(2026, 12, 31), date(2027, 1, 1)),
        (date(2027, 1, 1), date(2029, 1, 1)),  # a de 2027 já passou: a próxima é a dos prefeitos
        (date(2029, 1, 1), date(2031, 1, 1)),
    ],
)
def test_proxima_troca_de_titulares(dia, posse):
    assert proxima_posse(dia) == posse


def test_cada_vigencia_so_muda_no_dia_primeiro_de_janeiro():
    anterior = eleicoes_vigentes(date(2024, 1, 1))
    for ano in range(2024, 2034):
        for mes, dia in ((1, 1), (6, 15), (12, 31)):
            atual = eleicoes_vigentes(date(ano, mes, dia))
            if (mes, dia) != (1, 1):
                assert atual == eleicoes_vigentes(date(ano, 1, 1)), (ano, mes, dia)
        anterior = atual
    assert anterior["PREFEITO"] == 2032


def _zip_do_ano(ano: int) -> bytes:
    csv = "ANO_ELEICAO;SG_UF;SG_UE;DS_CARGO;SQ_CANDIDATO;NM_URNA_CANDIDATO;DS_SIT_TOT_TURNO\n"
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w") as z:
        z.writestr(f"consulta_cand_{ano}_TO.csv", csv.encode("latin-1"))
    return saida.getvalue()


class HttpFalso:
    def __init__(self):
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        return _zip_do_ano(int(url.rsplit("_", 1)[1].split(".")[0]))


@pytest.mark.parametrize(
    ("dia", "anos"),
    [
        (date(2026, 10, 21), {2024, 2022}),
        (date(2027, 1, 1), {2024, 2026}),
        (date(2029, 1, 1), {2028, 2026}),
    ],
)
def test_baixar_titulares_pede_o_zip_da_eleicao_vigente(dia, anos):
    http = HttpFalso()
    baixar_titulares(http, dia)
    assert {int(u.rsplit("_", 1)[1].split(".")[0]) for u in http.urls} == anos


def test_sem_data_usa_o_dia_de_hoje(monkeypatch):
    monkeypatch.setattr(tse_candidatos, "hoje", lambda: date(2027, 3, 1))
    http = HttpFalso()
    baixar_titulares(http)
    assert any("consulta_cand_2026.zip" in u for u in http.urls)


def test_hoje_usa_o_fuso_de_brasilia():
    from datetime import UTC, datetime

    # a posse é em 1º de janeiro no Brasil: à 1h UTC de 1/1/2027 ainda são 22h de 31/12/2026 em Brasília
    assert HOJE_REAL(datetime(2027, 1, 1, 1, 0, tzinfo=UTC)) == date(2026, 12, 31)
    assert HOJE_REAL(datetime(2027, 1, 1, 3, 0, tzinfo=UTC)) == date(2027, 1, 1)
    assert isinstance(HOJE_REAL(), date)
