"""
Testes unitários dos coletores do Bloco Governança — titulares eleitos (Task 30).
Nunca batem na rede: payload real gravado em tests/fixtures/governanca_payloads.py.
"""

import csv
import io
import re
import zipfile
from pathlib import Path

import pytest
from src.coletor_base.armazenamento import GerenciadorArmazenamentoRaw
from src.coletor_base.excecoes import FonteIndisponivelError, ValidacaoError
from tests.fixtures.governanca_payloads import CSV_TSE_TITULARES, fixture_tse_titulares

RAIZ = Path(__file__).parents[2]
CAMPOS_DIM_TITULAR = {
    "id_titular",
    "id_municipio",
    "cargo",
    "nome_titular",
    "ano_eleicao",
    "sq_candidato",
    "url_foto",
    "fonte",
    "id_fonte",
    "qualidade",
    "atualizado_em",
}


def _municipios_canonicos() -> set[str]:
    ddl = (RAIZ / "src" / "sql" / "ddl" / "dim_municipio.sql").read_text("utf-8")
    return set(re.findall(r"STRUCT\('(\d{7})' AS id_municipio", ddl))


def _coletor(tmp_path, extrair=None):
    from src.coletores.to_ger_01 import ColetorTOGER01

    c = ColetorTOGER01(ambiente="dev")
    c.armazenamento = GerenciadorArmazenamentoRaw(diretorio_local=tmp_path)
    if extrair is not None:
        c.extrair = extrair
    return c


def _zip_tse_com_pii(ano: int, cargo: str) -> bytes:
    """Monta, em memória, um zip no layout do TSE (latin-1, ';') com colunas pessoais extras."""
    linhas = [
        r
        for r in csv.DictReader(io.StringIO(CSV_TSE_TITULARES), delimiter=";")
        if r["DS_CARGO"] == cargo
    ]
    saida = io.StringIO()
    campos = [*linhas[0].keys(), "NR_CPF_CANDIDATO", "DS_EMAIL", "DT_NASCIMENTO"]
    w = csv.DictWriter(saida, campos, delimiter=";")
    w.writeheader()
    for r in linhas:
        w.writerow(
            {
                **r,
                "NR_CPF_CANDIDATO": "00000000000",
                "DS_EMAIL": "x@x",
                "DT_NASCIMENTO": "01/01/1970",
            }
        )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"consulta_cand_{ano}_TO.csv", saida.getvalue().encode("latin-1"))
    return buf.getvalue()


# ---------------------------------------------------------------- TO-GER-01


def test_to_ger_01_140_titulares(tmp_path):
    registros = _coletor(tmp_path).transformar(fixture_tse_titulares())
    assert len(registros) == 140
    assert sum(r["cargo"] == "PREFEITO" for r in registros) == 139
    assert sum(r["cargo"] == "GOVERNADOR" for r in registros) == 1


def test_to_ger_01_id_municipio_ibge_7_digitos_e_governador_null(tmp_path):
    registros = _coletor(tmp_path).transformar(fixture_tse_titulares())
    prefeitos = [r for r in registros if r["cargo"] == "PREFEITO"]
    assert {r["id_municipio"] for r in prefeitos} == _municipios_canonicos()
    gov = next(r for r in registros if r["cargo"] == "GOVERNADOR")
    assert gov["id_municipio"] is None and gov["id_titular"] == "GOVERNADOR:TO"


def test_to_ger_01_filtra_vice_e_nao_eleito(tmp_path):
    assert (
        "VICE" in CSV_TSE_TITULARES and "NÃO ELEITO" in CSV_TSE_TITULARES
    )  # fixture exercita o filtro
    registros = _coletor(tmp_path).transformar(fixture_tse_titulares())
    assert all(r["cargo"] in {"PREFEITO", "GOVERNADOR"} for r in registros)
    assert all(r["nome_titular"] for r in registros)


def test_to_ger_01_sem_brasao_marca_paleta_nem_dado_pessoal(tmp_path):
    for r in _coletor(tmp_path).transformar(fixture_tse_titulares()):
        assert set(r) == CAMPOS_DIM_TITULAR
        assert r["fonte"] == "TSE" and r["url_foto"] is None
    proibidos = re.compile(r"bras[aã]o|marca|paleta|cpf|email|nascimento|titulo", re.I)
    assert not any(proibidos.search(c) for c in CAMPOS_DIM_TITULAR)


def test_to_ger_01_extrair_minimiza_colunas_sem_rede(tmp_path, monkeypatch):
    from src.coletor_base import http

    zips = {
        "2024": _zip_tse_com_pii(2024, "PREFEITO"),
        "2022": _zip_tse_com_pii(2022, "GOVERNADOR"),
    }
    urls: list[str] = []

    def get_falso(self, url, headers=None):
        urls.append(url)
        return zips[re.search(r"_(\d{4})\.zip$", url).group(1)]

    monkeypatch.setattr(http.ClienteHTTP, "get", get_falso)
    monkeypatch.setattr(http.time, "sleep", lambda s: None)
    bruto = _coletor(tmp_path).extrair()
    cabecalho = bruto.decode("utf-8").splitlines()[0]
    assert "CPF" not in cabecalho and "EMAIL" not in cabecalho and "NASCIMENTO" not in cabecalho
    assert all(u.startswith("https://cdn.tse.jus.br/") for u in urls)
    assert len(_coletor(tmp_path).transformar(bruto)) == 140


def test_to_ger_01_executar_carrega_140_em_dim_titular(tmp_path):
    c = _coletor(tmp_path, extrair=fixture_tse_titulares)
    log = c.executar()
    assert log["status"] == "ok"
    tabela = c.carregador._mock_tabelas["dim_titular"]
    assert len(tabela) == 140
    assert all(len(r["hash_origem"]) == 64 for r in tabela.values())
    assert "fato_indicador" not in {k for k, v in c.carregador._mock_tabelas.items() if v}


def test_to_ger_01_falha_de_rede_preserva_ultimo_valido_defasado(tmp_path):
    c = _coletor(tmp_path, extrair=fixture_tse_titulares)
    c.executar()

    def falha():
        raise ConnectionError("timeout TSE")

    c.extrair = falha
    with pytest.raises(FonteIndisponivelError):
        c.executar()
    tabela = c.carregador._mock_tabelas["dim_titular"]
    assert len(tabela) == 140
    assert all(r["qualidade"] == "defasado" for r in tabela.values())
    assert all(r["nome_titular"] for r in tabela.values())  # nunca nulo/zero por falha


def test_to_ger_01_conformidade_antes_de_qualquer_requisicao(tmp_path, monkeypatch):
    from src.coletor_base import http
    from src.coletor_base.excecoes import ColetaBloqueadaError

    def get_proibido(self, url, headers=None):
        raise AssertionError("requisição de rede antes da guarda de conformidade")

    monkeypatch.setattr(http.ClienteHTTP, "get", get_proibido)
    c = _coletor(tmp_path)
    c.metadata_fonte = {"ID": "TO-GER-01", "RESTRIÇÃO ROBOTS/TERMOS": "Sim — teste"}
    with pytest.raises(ColetaBloqueadaError):
        c.executar()


def test_to_ger_01_rejeita_municipio_fora_dos_139(tmp_path):
    c = _coletor(tmp_path)
    registros = c.transformar(fixture_tse_titulares())
    registros[0]["id_municipio"] = "5300108"  # Brasília
    with pytest.raises(ValidacaoError):
        c.validar(registros)


# ------------------------------------------------------------ contratos


def test_contrato_max_55_linhas_governanca():
    for arq in ["to_ger_01.py", "to_ger_02.py"]:
        linhas = (RAIZ / "src" / "coletores" / arq).read_text("utf-8").splitlines()
        assert len(linhas) <= 55, f"{arq} excede limite de linhas ({len(linhas)})"


def test_contrato_nao_sobrescreve_executar_governanca():
    for arq in ["to_ger_01.py", "to_ger_02.py"]:
        conteudo = (RAIZ / "src" / "coletores" / arq).read_text("utf-8")
        assert "def executar(" not in conteudo, f"{arq} sobrescreve executar()"


# ---------------------------------------------------------------- TO-GER-02


def test_to_ger_02_bloqueado_antes_de_qualquer_requisicao(tmp_path, monkeypatch):
    from src.coletor_base import http
    from src.coletor_base.excecoes import ColetaBloqueadaError
    from src.coletores.to_ger_02 import ColetorTOGER02
    from tests.fixtures.governanca_payloads import RESPOSTA_DIVULGACANDCONTAS_ROBOTS_403

    assert "Access Denied" in RESPOSTA_DIVULGACANDCONTAS_ROBOTS_403  # evidência real do bloqueio

    def get_proibido(self, url, headers=None):
        raise AssertionError("TO-GER-02 não pode abrir conexão")

    monkeypatch.setattr(http.ClienteHTTP, "get", get_proibido)
    c = ColetorTOGER02(ambiente="dev")
    c.armazenamento = GerenciadorArmazenamentoRaw(diretorio_local=tmp_path)
    with pytest.raises(ColetaBloqueadaError, match=r"RF-71|link"):
        c.executar()
    with pytest.raises(ColetaBloqueadaError):
        c.extrair()
    assert not c.carregador._mock_tabelas.get("dim_titular")  # nada gravado


def test_to_ger_02_bloqueio_preserva_titulares_do_to_ger_01(tmp_path):
    """Falha/bloqueio do retrato não apaga nem zera os titulares já carregados (RF-66)."""
    from src.coletor_base.excecoes import ColetaBloqueadaError
    from src.coletores.to_ger_02 import ColetorTOGER02

    c1 = _coletor(tmp_path, extrair=fixture_tse_titulares)
    c1.executar()
    c2 = ColetorTOGER02(ambiente="dev")
    c2.carregador = c1.carregador
    with pytest.raises(ColetaBloqueadaError):
        c2.executar()
    tabela = c1.carregador._mock_tabelas["dim_titular"]
    assert len(tabela) == 140 and all(r["qualidade"] == "ok" for r in tabela.values())
