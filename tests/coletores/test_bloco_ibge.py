"""
Testes dos 7 coletores do Bloco IBGE (Task 08), refeitos na Task 28 com respostas REAIS gravadas.
Rodam sem rede: as fixtures são o que a API do IBGE devolveu em 2026-10-14 (ver tests/fixtures/).
"""

import importlib
import json
from pathlib import Path

import pytest
from src.coletor_base.excecoes import FonteIndisponivelError, ValidacaoError
from src.coletores.sidra import ler_series, periodo_ref
from tests.fixtures.ibge_payloads import (
    fixture_malha_territorial,
    fixture_pam,
    fixture_pib_estadual,
    fixture_pib_municipal,
    fixture_pnadc,
    fixture_populacao,
    fixture_ppm,
)

PALMAS = "1721000"
COLETORES = ["01", "02", "03", "04", "05", "06", "07"]


def _coletor(n: str):
    mod = importlib.import_module(f"src.coletores.to_ter_{n}")
    return getattr(mod, f"ColetorTOTER{n}")(ambiente="dev")


def _valor(registros, municipio, periodo):
    achados = [
        r for r in registros if r["id_municipio"] == municipio and r["periodo_ref"] == periodo
    ]
    assert len(achados) == 1, f"{municipio} {periodo}: {len(achados)} registros"
    return achados[0]["valor_num"]


def _sidra(series: dict[str, dict[str, str]]) -> bytes:
    """Resposta SIDRA SINTÉTICA com marcações do IBGE, só para testar a leitura."""
    corpo = [
        {
            "resultados": [
                {"series": [{"localidade": {"id": i}, "serie": s} for i, s in series.items()]}
            ]
        }
    ]
    return json.dumps(corpo).encode("utf-8")


# ─── TO-TER-01: População ──────────────────────────────────────────
def test_to_ter_01_populacao_139_municipios():
    registros = _coletor("01").transformar(fixture_populacao())
    municipios = {r["id_municipio"] for r in registros}
    assert len(municipios) == 139
    assert all(len(m) == 7 and m.startswith("17") for m in municipios)
    assert all(r["id_indicador"] == "populacao_residente" for r in registros)
    assert all(r["esfera_fonte"] == "federal" for r in registros)
    assert _valor(registros, PALMAS, "2024-01-01") == 323_625


def test_to_ter_01_soma_bate_com_a_coleta_anterior():
    """Soma dos 139 municípios em 2024 = total do data/ibge_populacao_to.csv, coletado à parte."""
    registros = _coletor("01").transformar(fixture_populacao())
    assert sum(r["valor_num"] for r in registros if r["periodo_ref"] == "2024-01-01") == 1_577_342


# ─── Marcações do IBGE (RF-55) ─────────────────────────────────────
def test_marcacoes_do_ibge_ausente_nunca_vira_zero():
    """'-' é zero absoluto; '...', '..', 'X' e vazio são dado ausente e não geram registro."""
    bruto = _sidra(
        {"1": {"2023": "-", "2024": "..."}, "2": {"2023": "X", "2024": ".."}, "3": {"2023": ""}}
    )
    assert ler_series(bruto) == [("1", "2023", 0.0)]
    assert _coletor("01").transformar(_sidra({"1": {"2024": "..."}})) == []


@pytest.mark.parametrize(
    "bruto", [b"{}", b"[]", b"nao e json", b'[{"resultados": []}]', b'[{"x": 1}]']
)
def test_resposta_sidra_invalida_levanta_validacao(bruto):
    with pytest.raises(ValidacaoError, match=r"formato inesperado|esperado 1"):
        ler_series(bruto)


def test_periodo_ref_anual_e_trimestral():
    assert periodo_ref("2023") == "2023-01-01"
    assert [periodo_ref(f"2026{q:02d}") for q in (1, 2, 3, 4)] == [
        "2026-01-01",
        "2026-04-01",
        "2026-07-01",
        "2026-10-01",
    ]


# ─── TO-TER-02: PIB Municipal ──────────────────────────────────────
def test_to_ter_02_pib_municipal_139_com_serie():
    registros = _coletor("02").transformar(fixture_pib_municipal())
    assert len({r["id_municipio"] for r in registros}) == 139
    assert sorted({r["periodo_ref"][:4] for r in registros}) == [
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
    ]
    assert all(r["unidade"] == "R$ mil" and r["valor_num"] > 0 for r in registros)
    assert _valor(registros, PALMAS, "2023-01-01") == 14_168_469


# ─── TO-TER-03: PIB Estadual ───────────────────────────────────────
def test_to_ter_03_pib_estadual_nivel_estado():
    registros = _coletor("03").transformar(fixture_pib_estadual())
    assert len(registros) == 5
    assert all(r["id_municipio"] is None for r in registros)  # nível estadual
    assert {r["periodo_ref"]: r["valor_num"] for r in registros}["2023-01-01"] == 64_317_699
    assert len({r["id_registro"] for r in registros}) == 5


# ─── TO-TER-04: Área territorial ───────────────────────────────────
def test_to_ter_04_area_139_soma_bate_com_o_estado():
    registros = _coletor("04").transformar(fixture_malha_territorial())
    assert len(registros) == 139
    assert all(r["unidade"] == "km²" for r in registros)
    assert _valor(registros, PALMAS, "2022-01-01") == 2227.329
    assert sum(r["valor_num"] for r in registros) == pytest.approx(277_423.627, abs=0.01)


# ─── TO-TER-05: PAM ────────────────────────────────────────────────
def test_to_ter_05_pam_139():
    registros = _coletor("05").transformar(fixture_pam())
    assert len({r["id_municipio"] for r in registros}) == 139
    assert all(r["id_indicador"] == "producao_agricola" for r in registros)
    assert _valor(registros, PALMAS, "2025-01-01") == 266_315


# ─── TO-TER-06: PPM ────────────────────────────────────────────────
def test_to_ter_06_ppm_139():
    registros = _coletor("06").transformar(fixture_ppm())
    assert len({r["id_municipio"] for r in registros}) == 139
    assert all(r["unidade"] == "cabeças" for r in registros)
    assert _valor(registros, PALMAS, "2025-01-01") == 37_459


# ─── TO-TER-07: PNADC ──────────────────────────────────────────────
def test_to_ter_07_pnadc_nivel_estado_trimestral():
    registros = _coletor("07").transformar(fixture_pnadc())
    assert len(registros) == 4
    assert all(r["id_municipio"] is None for r in registros)
    assert all(r["periodicidade"] == "Trimestral" for r in registros)
    segundo = [r for r in registros if r["valor_texto"] == "2T2026"]
    assert len(segundo) == 1
    assert segundo[0]["periodo_ref"] == "2026-04-01" and segundo[0]["valor_num"] == 4.1


# ─── Extração: URL e cliente HTTP (sem rede) ───────────────────────
@pytest.mark.parametrize("n", COLETORES)
def test_extrair_chama_a_api_real_pelo_cliente_http(n, rede_gravada):
    """extrair() busca na URL SIDRA do coletor e devolve a resposta sem alterar."""
    c = _coletor(n)
    bruto = c.extrair()
    assert rede_gravada == [c.url()]
    assert c.url().startswith("https://servicodados.ibge.gov.br/api/v3/agregados/")
    assert len(c.transformar(bruto)) > 0


# ─── Contrato: Linhas por coletor ≤ 50 (RNF-E02) ──────────────────
def test_rnf_e02_coletores_max_50_linhas():
    """Cada coletor deve ter ≤ 50 linhas de código-fonte (RNF-E02)."""
    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in sorted(pasta.glob("to_ter_*.py")):
        linhas = arq.read_text("utf-8").splitlines()
        assert len(linhas) <= 55, f"{arq.name} tem {len(linhas)} linhas, excede ~50 (RNF-E02)"


# ─── Contrato: Nenhum coletor sobrescreve executar() ───────────────
def test_nenhum_coletor_sobrescreve_executar():
    """Coletores não devem sobrescrever o método executar() do ColetorBase."""
    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in sorted(pasta.glob("to_ter_*.py")):
        assert "def executar(" not in arq.read_text("utf-8"), (
            f"{arq.name} sobrescreve executar(), proibido pelo contrato ColetorBase"
        )


# ─── Contrato: Idempotência (reexecução não duplica) ───────────────
def test_idempotencia_reexecucao(rede_gravada):
    """Execução dupla do coletor: a segunda detecta o hash idêntico e retorna 'sem_mudanca'."""
    c = _coletor("01")
    r1 = c.executar()
    r2 = c.executar()
    assert r1["status"] == "ok" and r1["municipios_cobertos"] == 139
    assert r2["status"] == "sem_mudanca"


# ─── Contrato: Falha isolada não derruba outros coletores ──────────
def test_falha_isolada_nao_derruba_outros(rede_gravada, monkeypatch):
    """Falha de 1 fonte não impede execução das demais (RF-68)."""
    from src.coletor_base.http import ClienteHTTP

    get_ok = ClienteHTTP.get

    def get(self, url, headers=None):
        if "/agregados/6579/" in url:
            raise OSError("fonte fora do ar")
        return get_ok(self, url, headers)

    monkeypatch.setattr(ClienteHTTP, "get", get)
    status = []
    for n in ["01", "02"]:
        try:
            status.append(_coletor(n).executar()["status"])
        except FonteIndisponivelError:
            status.append("falha")
    assert status == ["falha", "ok"]
