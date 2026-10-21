"""
Sentinelas das 9 fontes (Task 35, passo 4): a consulta barata que diz se há dado novo.
Respostas REAIS gravadas em 21/10/2026 (tests/fixtures/gravadas/), sem rede.
"""

import importlib
import json
from datetime import date

import pytest
import urllib3
from src.cli import REGISTRO_COLETORES
from src.coletor_base.http import ClienteHTTP
from src.orquestracao.fontes import FONTES, IMPLEMENTADOS, TITULARES
from src.orquestracao.sentinelas import Sentinela, SentinelaError, Sentinelas
from tests.fixtures.ibge_payloads import fixture_extrato_siconfi

HOJE = date(2026, 10, 21)


@pytest.fixture
def get(rede_gravada):
    return ClienteHTTP(delay_segundos=0).get  # a rede simulada responde com as gravações reais


def _sentinelas(get, hoje=HOJE):
    return Sentinelas(get, hoje)


# --- IBGE ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fonte", "marca", "periodo"),
    [
        (
            "TO-TER-01",
            "2026|2026-08-28",
            "2026",
        ),  # estimativas de população, divulgadas em 28/08/2026
        ("TO-TER-02", "2023|2025-12-19", "2023"),  # Contas Regionais / PIB dos Municípios
        ("TO-TER-03", "2023|2025-12-19", "2023"),
        ("TO-TER-04", "2022|2026-05-07", "2022"),  # área territorial: um único período (Censo 2022)
        ("TO-TER-05", "2025|2026-10-01", "2025"),  # PAM
        ("TO-TER-06", "2025|2026-09-30", "2025"),  # PPM
        ("TO-TER-07", "202602|2026-08-14", "202602"),  # PNAD Contínua trimestral
    ],
)
def test_marca_do_ibge_e_o_ultimo_periodo_com_a_data_de_modificacao(get, fonte, marca, periodo):
    s = _sentinelas(get).consultar(fonte)
    assert isinstance(s, Sentinela)
    assert (s.marca, s.ultimo_periodo) == (marca, periodo)


def test_pib_municipal_e_estadual_compartilham_uma_so_consulta(get, rede_gravada):
    s = _sentinelas(get)
    s.consultar("TO-TER-02")
    s.consultar("TO-TER-03")
    assert [u for u in rede_gravada if u.endswith("/agregados/5938/periodos")] == [
        "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos"
    ]


def test_marca_muda_quando_o_ibge_revisa_o_mesmo_periodo(get):
    """Revisão (nova data de modificação) sem período novo também conta como novidade."""

    def get_revisado(url):
        lista = json.loads(get(url))
        lista[-1]["modificacao"] = "02/11/2026"
        return json.dumps(lista).encode()

    antes = _sentinelas(get).consultar("TO-TER-05").marca
    depois = _sentinelas(get_revisado).consultar("TO-TER-05").marca
    assert (antes, depois) == ("2025|2026-10-01", "2025|2026-11-02")


def test_marca_muda_quando_sai_um_periodo_novo(get):
    def get_novo(url):
        lista = json.loads(get(url))
        lista.append({"id": "2026", "literals": ["2026"], "modificacao": "30/09/2027"})
        return json.dumps(lista).encode()

    assert _sentinelas(get_novo).consultar("TO-TER-06").marca == "2026|2027-09-30"


def test_ultimo_periodo_e_o_maior_mesmo_com_a_lista_fora_de_ordem(get):
    def get_embaralhado(url):
        return json.dumps(list(reversed(json.loads(get(url))))).encode()

    assert _sentinelas(get_embaralhado).consultar("TO-TER-07").ultimo_periodo == "202602"


# --- calendário do IBGE (próxima divulgação) ---------------------------------------------------------


@pytest.mark.parametrize(
    ("hoje", "proxima"),
    [
        (date(2026, 10, 21), "2026-11-18"),
        (date(2026, 11, 18), "2026-11-18"),  # no dia da divulgação ainda é a próxima
        (date(2026, 11, 19), "2027-02-19"),
        (date(2027, 2, 20), None),  # nada mais no calendário
    ],
)
def test_proxima_divulgacao_da_pnad_vem_do_calendario(get, hoje, proxima):
    assert _sentinelas(get, hoje).consultar("TO-TER-07").proxima_divulgacao == proxima


def test_so_a_pnad_consulta_o_calendario(get, rede_gravada):
    for fonte in ("TO-TER-01", "TO-TER-02", "TO-TER-04", "TO-TER-05", "TO-TER-06"):
        assert _sentinelas(get).consultar(fonte).proxima_divulgacao is None
    assert not [u for u in rede_gravada if "/calendario/" in u]


def test_calendario_fora_do_ar_nao_derruba_a_sentinela(get):
    def get_sem_calendario(url):
        if "/calendario/" in url:
            raise urllib3.exceptions.HTTPError("503")
        return get(url)

    s = _sentinelas(get_sem_calendario).consultar("TO-TER-07")
    assert s.marca == "202602|2026-08-14" and s.proxima_divulgacao is None
    assert "calendário" in s.aviso


# --- SICONFI ------------------------------------------------------------------------------------


def _entregas_relevantes(ano):
    itens = json.loads(fixture_extrato_siconfi(ano))["items"]
    return [
        i
        for i in itens
        if (i["entregavel"].startswith("Relatório Resumido") and i["periodo"] == 6)
        or i["entregavel"].startswith("Relatório de Gestão Fiscal")
    ]


def test_siconfi_marca_e_a_ultima_entrega_e_quantas_foram(get, rede_gravada):
    s = _sentinelas(get).consultar("TO-REC-02")
    entregas = [e for ano in (2023, 2024, 2025) for e in _entregas_relevantes(ano)]
    assert s.marca == f"{max(e['data_status'][:10] for e in entregas)}|{len(entregas)}"
    assert s.marca.startswith("2026-02-25|") and s.ultimo_periodo == "2025"
    assert s.proxima_divulgacao is None
    urls = [u for u in rede_gravada if "extrato_entregas" in u]
    assert [u.split("an_referencia=")[1] for u in urls] == [
        "2023",
        "2024",
        "2025",
    ]  # os exercícios do coletor
    assert all("id_ente=17" in u for u in urls)  # só o estado: 1 consulta por exercício, não 140


def test_siconfi_so_olha_os_exercicios_que_o_coletor_usa():
    pedidos = []

    def get_vazio(url):
        pedidos.append(url.split("an_referencia=")[1])
        return b'{"hasMore": false, "items": []}'

    s = Sentinelas(get_vazio, date(2027, 1, 5)).consultar("TO-REC-02")
    assert pedidos == ["2024", "2025", "2026"]  # ano passado e os 2 anteriores, como coletar_rcl
    assert s.marca == "sem-entregas|0" and s.ultimo_periodo is None


def test_siconfi_entrega_nova_ou_retificacao_muda_a_marca(get):
    def get_com_retificacao(url):
        d = json.loads(get(url))
        if url.endswith("an_referencia=2025"):
            d["items"].append(
                {
                    **d["items"][0],
                    "data_status": "2026-10-20T10:00:00Z",
                    "entregavel": "Relatório de Gestão Fiscal",
                }
            )
        return json.dumps(d).encode()

    antes = _sentinelas(get).consultar("TO-REC-02").marca
    depois = _sentinelas(get_com_retificacao).consultar("TO-REC-02").marca
    assert antes != depois and depois.startswith("2026-10-20|")


def test_siconfi_entrega_de_bimestre_do_ano_corrente_nao_e_novidade(get):
    """RREO dos bimestres 1 a 5 não entram no coletor (só o 6º, anual): não podem disparar coleta."""

    def get_bimestre(url):
        d = json.loads(get(url))
        if url.endswith("an_referencia=2025"):
            d["items"].append(
                {
                    **d["items"][0],
                    "data_status": "2026-10-20T10:00:00Z",
                    "entregavel": "Relatório Resumido de Execução Orçamentária",
                    "periodo": 3,
                }
            )
        return json.dumps(d).encode()

    assert (
        _sentinelas(get_bimestre).consultar("TO-REC-02").marca
        == _sentinelas(get).consultar("TO-REC-02").marca
    )


def test_siconfi_resposta_paginada_e_recusada():
    with pytest.raises(SentinelaError, match="paginou"):
        Sentinelas(lambda url: b'{"hasMore": true, "items": []}', HOJE).consultar("TO-REC-02")


# --- TSE ----------------------------------------------------------------------------------------


def _sem_rede(url):
    raise AssertionError(f"o TSE não consulta rede na sentinela: {url}")


@pytest.mark.parametrize(
    ("hoje", "marca", "periodo", "proxima"),
    [
        (date(2026, 10, 21), "GOVERNADOR=2022|PREFEITO=2024", "2024", "2027-01-01"),
        (date(2026, 12, 31), "GOVERNADOR=2022|PREFEITO=2024", "2024", "2027-01-01"),
        (date(2027, 1, 1), "GOVERNADOR=2026|PREFEITO=2024", "2026", "2029-01-01"),
        (date(2029, 1, 1), "GOVERNADOR=2026|PREFEITO=2028", "2028", "2031-01-01"),
    ],
)
def test_tse_marca_pela_data_sem_consultar_rede(hoje, marca, periodo, proxima):
    s = Sentinelas(_sem_rede, hoje).consultar(TITULARES)
    assert (s.marca, s.ultimo_periodo, s.proxima_divulgacao) == (marca, periodo, proxima)


def test_marca_do_tse_muda_so_na_virada_do_mandato():
    antes = Sentinelas(_sem_rede, date(2026, 12, 31)).consultar(TITULARES).marca
    depois = Sentinelas(_sem_rede, date(2027, 1, 1)).consultar(TITULARES).marca
    assert antes != depois


# --- robustez -----------------------------------------------------------------------------------


def test_mapa_de_agregados_acompanha_os_coletores():
    """Se alguém trocar o agregado de um coletor, a sentinela não pode continuar olhando o antigo."""
    for fonte in IMPLEMENTADOS[:-1]:  # as 7 do IBGE
        modulo, classe = REGISTRO_COLETORES[fonte]
        assert (
            Sentinelas.AGREGADOS[fonte] == getattr(importlib.import_module(modulo), classe).agregado
        ), fonte
    assert set(Sentinelas.AGREGADOS) == set(IMPLEMENTADOS[:-1])


def test_fonte_desconhecida_e_recusada(get):
    with pytest.raises(SentinelaError, match="desconhecida"):
        _sentinelas(get).consultar("TO-XXX-99")


@pytest.mark.parametrize(
    "resposta",
    [
        b"",
        b"nao e json",
        b"{}",
        b"[]",
        b'[{"id": "2025"}]',
        b'[{"modificacao": "01/01/2025"}]',
        b'[{"id": "2025", "modificacao": "ontem"}]',
        b'["2025"]',
    ],
)
def test_resposta_ibge_invalida_vira_erro_claro(resposta):
    with pytest.raises(SentinelaError, match="TO-TER-01"):
        Sentinelas(lambda url: resposta, HOJE).consultar("TO-TER-01")


@pytest.mark.parametrize(
    "erro",
    [
        OSError("sem rede"),
        urllib3.exceptions.HTTPError("HTTP 503"),
        urllib3.exceptions.MaxRetryError(None, "u"),
    ],
)
def test_falha_de_rede_vira_sentinela_error_com_a_fonte(erro):
    def get_falha(url):
        raise erro

    with pytest.raises(SentinelaError, match="TO-REC-02"):
        Sentinelas(get_falha, HOJE).consultar("TO-REC-02")


def test_todas_as_fontes_tem_sentinela(get):
    s = _sentinelas(get)
    for fonte in FONTES:
        assert s.consultar(fonte).marca
