"""
scripts/exportar_painel.py (Task 29): dados reais dos coletores no formato que o painel lê.
Rodam sem rede (rede_gravada): IBGE e SICONFI respondem com as respostas reais gravadas.
"""

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from src.coletor_base.http import ClienteHTTP
from src.coletores import siconfi, tse_candidatos

RAIZ = Path(__file__).parents[1]
PALMAS, ABREULANDIA, AGUIARNOPOLIS, GURUPI = "1721000", "1700251", "1700301", "1709500"


def _script():
    spec = importlib.util.spec_from_file_location(
        "exportar_painel", RAIZ / "scripts" / "exportar_painel.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def hoje_2026(monkeypatch):
    """Congela o 'agora' do SICONFI em 2026: os exercícios pedidos ficam 2023 a 2025."""

    class Agora(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 14, tzinfo=UTC)

    monkeypatch.setattr(siconfi, "datetime", Agora)


def _exportar(tmp_path, *argumentos):
    saida = tmp_path / "painel_dados.json"
    codigo = _script().main([*argumentos, "--saida", str(saida)])
    return codigo, saida


def test_exporta_as_9_fontes_no_formato_do_painel(rede_gravada, hoje_2026, tmp_path):
    codigo, saida = _exportar(tmp_path)
    assert codigo == 0
    d = json.loads(saida.read_text("utf-8"))
    assert {f: m["status"] for f, m in d["fontes"].items()} == dict.fromkeys(d["fontes"], "ok")
    assert len(d["fontes"]) == 9 and len(d["municipios"]) == 139
    assert d["fontes"]["TO-TER-01"]["registros"] == 139 * 3
    # município: série [[rótulo, valor], ...] em ordem cronológica
    palmas = d["municipios"][PALMAS]
    assert [a for a, _ in palmas["pib_municipal"]] == ["2019", "2020", "2021", "2022", "2023"]
    assert palmas["pib_municipal"][-1] == ["2023", 14_168_469.0]
    assert palmas["populacao_residente"][0] == ["2024", 323_625.0]
    assert palmas["receita_corrente_liquida"] == [
        ["2024", pytest.approx(2_045_511.03951)],
        ["2025", pytest.approx(2_155_602.77972)],
    ]
    assert d["unidades"]["pib_municipal"] == "R$ mil" and d["unidades"]["area_territorial"] == "km²"


def test_estado_vem_direto_da_fonte_ou_da_soma_dos_139_municipios(
    rede_gravada, hoje_2026, tmp_path
):
    _, saida = _exportar(tmp_path)
    estado = json.loads(saida.read_text("utf-8"))["estado"]
    assert estado["pib_estadual"][-1] == ["2023", 64_317_699.0]
    assert estado["taxa_desocupacao"][-1] == ["2T2026", 4.1]  # trimestral: o rótulo é o trimestre
    assert estado["receita_corrente_liquida"][-1] == ["2025", pytest.approx(15_568_042.57326)]
    # somas com cobertura de 139/139, iguais ao total oficial do IBGE
    assert estado["populacao_residente"][0] == ["2024", 1_577_342.0]
    assert estado["area_territorial"] == [["2022", pytest.approx(277_423.631)]]
    assert estado["rebanho_bovino"][-1] == ["2025", 11_532_757.0]


def test_municipio_que_nao_publicou_fica_sem_o_indicador(rede_gravada, hoje_2026, tmp_path):
    """Aguiarnópolis não publicou RREO nem RGF: a chave não existe (o painel mostra 'Sem dado', nunca zero)."""
    _, saida = _exportar(tmp_path)
    municipios = json.loads(saida.read_text("utf-8"))["municipios"]
    assert "receita_corrente_liquida" not in municipios[AGUIARNOPOLIS]
    assert "pib_municipal" in municipios[AGUIARNOPOLIS]


def test_municipio_pequeno_tem_a_rcl_pelo_rgf(rede_gravada, hoje_2026, tmp_path):
    """Abreulândia entrega o RREO Simplificado (sem Anexo 3): a RCL vem do RGF, já em R$ mil."""
    _, saida = _exportar(tmp_path)
    d = json.loads(saida.read_text("utf-8"))
    assert d["municipios"][ABREULANDIA]["receita_corrente_liquida"] == [
        ["2024", pytest.approx(29_498.40645)],
        ["2025", pytest.approx(34_960.55996)],
    ]
    assert (
        d["fontes"]["TO-REC-02"]["registros"] == 8
    )  # estado, Palmas, Araguaína e Abreulândia x 2 anos


def test_falha_de_uma_fonte_nao_derruba_as_outras(rede_gravada, hoje_2026, monkeypatch, tmp_path):
    ok = ClienteHTTP.get

    def get(self, url, headers=None):
        if "/agregados/6579/" in url:
            raise OSError("fonte fora do ar")
        return ok(self, url, headers)

    monkeypatch.setattr(ClienteHTTP, "get", get)
    codigo, saida = _exportar(tmp_path)
    d = json.loads(saida.read_text("utf-8"))
    assert codigo == 0
    assert (
        d["fontes"]["TO-TER-01"]["status"] == "erro"
        and "fora do ar" in d["fontes"]["TO-TER-01"]["erro"]
    )
    assert d["fontes"]["TO-TER-02"]["status"] == "ok"
    assert "populacao_residente" not in d["estado"]
    assert "populacao_residente" not in d["municipios"][PALMAS]


def test_nenhuma_fonte_ok_nao_toca_o_arquivo(monkeypatch, tmp_path):
    saida = tmp_path / "painel_dados.json"
    saida.write_text('{"intacto": true}', "utf-8")

    def get(self, url, headers=None):
        raise OSError("sem rede")

    monkeypatch.setattr(ClienteHTTP, "get", get)
    assert _script().main(["--saida", str(saida)]) == 1
    assert json.loads(saida.read_text("utf-8")) == {"intacto": True}


def test_pular_reaproveita_a_fonte_do_arquivo_anterior(rede_gravada, hoje_2026, tmp_path):
    _, saida = _exportar(tmp_path)
    antes = json.loads(saida.read_text("utf-8"))
    chamadas_antes = len(rede_gravada)
    codigo, _ = _exportar(tmp_path, "--pular", "TO-REC-02")
    depois = json.loads(saida.read_text("utf-8"))
    assert codigo == 0
    assert not any("tesouro" in u for u in rede_gravada[chamadas_antes:])  # não foi ao SICONFI
    assert depois["fontes"]["TO-REC-02"] == antes["fontes"]["TO-REC-02"]
    assert (
        depois["estado"]["receita_corrente_liquida"] == antes["estado"]["receita_corrente_liquida"]
    )
    assert (
        depois["municipios"][PALMAS]["receita_corrente_liquida"]
        == antes["municipios"][PALMAS]["receita_corrente_liquida"]
    )


def test_pular_sem_arquivo_anterior_marca_a_fonte_como_erro(rede_gravada, tmp_path):
    _, saida = _exportar(tmp_path, "--pular", "TO-REC-02")
    d = json.loads(saida.read_text("utf-8"))
    assert d["fontes"]["TO-REC-02"]["status"] == "erro"
    assert "receita_corrente_liquida" not in d["estado"]


# --- Task 32: titulares eleitos (TO-GER-01, TSE) ---


def test_titulares_eleitos_vao_para_o_painel(rede_gravada, hoje_2026, tmp_path):
    """139 prefeitos + governador, só com nome, cargo, ano e fonte (sem sq_candidato nem url_foto)."""
    _, saida = _exportar(tmp_path)
    d = json.loads(saida.read_text("utf-8"))
    titulares = d["titulares"]
    assert (
        d["fontes"]["TO-GER-01"]["status"] == "ok" and d["fontes"]["TO-GER-01"]["registros"] == 140
    )
    assert len(titulares["municipios"]) == 139 and set(titulares["municipios"]) == set(
        d["municipios"]
    )
    assert titulares["municipios"][PALMAS] == {
        "nome": "EDUARDO SIQUEIRA CAMPOS",
        "cargo": "PREFEITO",
        "ano_eleicao": 2024,
        "fonte": "TSE",
    }
    assert titulares["municipios"][GURUPI]["nome"] == "JOSI NUNES"
    assert titulares["estado"] == {
        "nome": "WANDERLEI BARBOSA",
        "cargo": "GOVERNADOR",
        "ano_eleicao": 2022,
        "fonte": "TSE",
    }


def test_titulares_invalidos_nao_sao_gravados(rede_gravada, hoje_2026, monkeypatch, tmp_path):
    """Se o filtro deixasse passar não eleitos (3 governadores, prefeitos duplicados), nada é gravado."""
    monkeypatch.setattr(
        tse_candidatos,
        "eh_titular_to",
        lambda r: r["SG_UF"] == "TO" and r["DS_CARGO"] in tse_candidatos.ELEICOES,
    )
    codigo, saida = _exportar(tmp_path)
    d = json.loads(saida.read_text("utf-8"))
    assert codigo == 0
    assert d["fontes"]["TO-GER-01"]["status"] == "erro"
    assert "ValidacaoError" in d["fontes"]["TO-GER-01"]["erro"]
    assert "titulares" not in d
    assert d["fontes"]["TO-TER-01"]["status"] == "ok"


def test_falha_do_tse_nao_derruba_as_outras_fontes(rede_gravada, hoje_2026, monkeypatch, tmp_path):
    ok = ClienteHTTP.get

    def get(self, url, headers=None):
        if "cdn.tse.jus.br" in url:
            raise OSError("TSE fora do ar")
        return ok(self, url, headers)

    monkeypatch.setattr(ClienteHTTP, "get", get)
    codigo, saida = _exportar(tmp_path)
    d = json.loads(saida.read_text("utf-8"))
    assert codigo == 0
    assert d["fontes"]["TO-GER-01"]["status"] == "erro" and "titulares" not in d
    assert sum(m["status"] == "ok" for m in d["fontes"].values()) == 8


def test_pular_reaproveita_os_titulares(rede_gravada, hoje_2026, tmp_path):
    _, saida = _exportar(tmp_path)
    antes = json.loads(saida.read_text("utf-8"))
    chamadas_antes = len(rede_gravada)
    codigo, _ = _exportar(tmp_path, "--pular", "TO-GER-01")
    depois = json.loads(saida.read_text("utf-8"))
    assert codigo == 0
    assert not any("tse.jus.br" in u for u in rede_gravada[chamadas_antes:])  # não foi ao TSE
    assert depois["titulares"] == antes["titulares"]
    assert depois["fontes"]["TO-GER-01"] == antes["fontes"]["TO-GER-01"]
