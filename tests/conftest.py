"""Rede simulada com as respostas REAIS gravadas: os testes dos coletores rodam sem internet."""

import io
import json
import zipfile

import pytest
from src.coletor_base.http import ClienteHTTP
from src.coletores import siconfi
from tests.fixtures.governanca_payloads import CSV_TSE_TITULARES
from tests.fixtures.ibge_payloads import (
    fixture_malha_territorial,
    fixture_pam,
    fixture_pib_estadual,
    fixture_pib_municipal,
    fixture_pnadc,
    fixture_populacao,
    fixture_ppm,
)
from tests.fixtures.recursos_payloads import fixture_siconfi_rcl, fixture_siconfi_rgf


def _municipios(url: str) -> bytes:
    """Lista de localidades do IBGE: os 139 códigos reais que aparecem na fixture de população."""
    ids = sorted(
        {
            s["localidade"]["id"]
            for s in json.loads(fixture_populacao())[0]["resultados"][0]["series"]
        }
    )
    return json.dumps([{"id": int(i)} for i in ids]).encode()


def _rreo(url: str) -> bytes:
    """RREO do SICONFI: só estado, Palmas e Araguaína publicaram (2024 e 2025); os demais vêm vazios."""
    ente = int(url.rsplit("id_ente=", 1)[1])
    ano = int(url.split("an_exercicio=")[1].split("&")[0])
    itens = [
        {**i, "cod_conta": siconfi.CONTA_RREO, "coluna": siconfi.COLUNA_RREO}
        for i in json.loads(fixture_siconfi_rcl())["itens"]
        if i["cod_ibge"] == ente and i["exercicio"] == ano
    ]
    return json.dumps({"hasMore": False, "items": itens}).encode()


def _rgf(url: str) -> bytes:
    """RGF do SICONFI: só o Simplificado semestral de Abreulândia (2024 e 2025) publicou; o quadrimestral vem vazio."""
    ente = int(url.split("id_ente=")[1].split("&")[0])
    ano = int(url.split("an_exercicio=")[1].split("&")[0])
    simplificado = "RGF%20Simplificado" in url
    itens = [
        {**i, "cod_conta": siconfi.CONTA_RGF, "coluna": siconfi.COLUNA_RGF}
        for i in json.loads(fixture_siconfi_rgf())["itens"]
        if simplificado and i["cod_ibge"] == ente and i["exercicio"] == ano
    ]
    return json.dumps({"hasMore": False, "items": itens}).encode()


def _tse(url: str) -> bytes:
    """Zip consulta_cand_{ano} do TSE, montado com as linhas daquele ano do recorte real (latin-1, ';')."""
    ano = url.rsplit("consulta_cand_", 1)[1].split(".zip")[0]
    cabecalho, *linhas = CSV_TSE_TITULARES.splitlines()
    csv = "\n".join([cabecalho, *(lin for lin in linhas if lin.startswith(ano + ";"))])
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w") as z:
        z.writestr(f"consulta_cand_{ano}_TO.csv", csv.encode("latin-1"))
    return saida.getvalue()


# (trechos que a URL precisa conter, função que devolve a resposta gravada)
ROTAS = [
    (("/agregados/6579/",), lambda url: fixture_populacao()),
    (("/agregados/5938/", "localidades=N6"), lambda url: fixture_pib_municipal()),
    (("/agregados/5938/", "localidades=N3"), lambda url: fixture_pib_estadual()),
    (("/agregados/4714/",), lambda url: fixture_malha_territorial()),
    (("/agregados/5457/", "classificacao=782[0]"), lambda url: fixture_pam()),
    (("/agregados/3939/", "classificacao=79[2670]"), lambda url: fixture_ppm()),
    (("/agregados/4099/",), lambda url: fixture_pnadc()),
    ((siconfi.URL_MUNICIPIOS,), _municipios),
    (("apidatalake.tesouro.gov.br", "/rreo?"), _rreo),
    (("apidatalake.tesouro.gov.br", "/rgf?"), _rgf),
    (("cdn.tse.jus.br", "/consulta_cand_"), _tse),
]


@pytest.fixture(autouse=True)
def _sem_internet(monkeypatch):
    """Nenhum teste acessa a internet: quem precisa de resposta usa rede_gravada ou o próprio monkeypatch."""

    def bloqueado(self, url, headers=None):
        raise AssertionError(f"Teste tentou acessar a internet: {url}")

    monkeypatch.setattr(ClienteHTTP, "get", bloqueado)


@pytest.fixture
def rede_gravada(monkeypatch, tmp_path):
    """ClienteHTTP.get devolve a resposta gravada e a zona raw (.data_raw) vai para tmp_path."""
    monkeypatch.chdir(tmp_path)
    chamadas: list[str] = []

    def get(self, url, headers=None):
        chamadas.append(url)
        for trechos, resposta in ROTAS:
            if all(t in url for t in trechos):
                return resposta(url)
        raise AssertionError(f"URL sem resposta gravada: {url}")

    monkeypatch.setattr(ClienteHTTP, "get", get)
    return chamadas
