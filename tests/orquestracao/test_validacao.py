"""
Regras de validação do orquestrador (Task 35, passo 7), decisões do Bruno:
  - IBGE e TSE: 139 municípios (100%); SICONFI: estado obrigatório, município atrasado não bloqueia;
  - 3σ só em agregados estaduais e séries estruturais, sobre a VARIAÇÃO entre períodos;
  - municipais voláteis: só integridade.
O backtest roda nas séries reais gravadas (tests/fixtures/gravadas/sidra_hist_*.json).
"""

import copy
import math
from pathlib import Path

import pytest
from src.coletores.to_ter_01 import ColetorTOTER01
from src.coletores.to_ter_03 import ColetorTOTER03
from src.coletores.to_ter_07 import ColetorTOTER07
from src.orquestracao import validacao
from src.orquestracao.fontes import FONTES, IMPLEMENTADOS, TITULARES
from src.orquestracao.painel import instanciar
from src.orquestracao.validacao import (
    POLITICA_3SIGMA,
    ColetaRecusada,
    backtest,
    classificar_ponto,
    validar_cobertura_ibge,
    validar_fonte,
    validar_rcl,
    variacoes,
)

GRAVADAS = Path(__file__).parents[1] / "fixtures" / "gravadas"


@pytest.fixture(autouse=True)
def _ano_do_siconfi(monkeypatch):
    from datetime import UTC, datetime

    from src.coletores import siconfi

    class Agora(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 14, tzinfo=UTC)

    monkeypatch.setattr(siconfi, "datetime", Agora)


@pytest.fixture
def registros(rede_gravada):
    saida = {}
    for f in FONTES:
        c = instanciar(f)
        saida[f] = c.transformar(c.extrair())
    return saida


def _serie_real(arquivo, classe, **attrs):
    """Série do estado [[rótulo, valor], ...] a partir da resposta gravada (a mesma conversão do painel)."""
    c = classe(ambiente="dev")
    for k, v in attrs.items():
        setattr(c, k, v)
    recs = c.transformar((GRAVADAS / arquivo).read_bytes())
    return [
        [r["valor_texto"] or r["periodo_ref"][:4], r["valor_num"]]
        for r in sorted(recs, key=lambda r: r["periodo_ref"])
        if r["id_municipio"] is None
    ]


@pytest.fixture(scope="module")
def series_reais():
    return {
        "TO-TER-01": _serie_real(
            "sidra_hist_populacao_estado.json", ColetorTOTER01, localidades="N3[17]"
        ),
        "TO-TER-03": _serie_real("sidra_hist_pib_estadual.json", ColetorTOTER03),
        "TO-TER-07": _serie_real("sidra_hist_desocupacao.json", ColetorTOTER07),
    }


# --- variações e classificação ------------------------------------------------------------------


def test_variacao_percentual_e_em_pontos():
    s = [["2020", 100.0], ["2021", 110.0], ["2022", 99.0]]
    assert variacoes(s, "pct") == [("2021", pytest.approx(10.0)), ("2022", pytest.approx(-10.0))]
    assert variacoes(s, "abs") == [("2021", pytest.approx(10.0)), ("2022", pytest.approx(-11.0))]


def test_variacao_percentual_pula_base_zero_sem_dividir_por_zero():
    assert variacoes([["2020", 0.0], ["2021", 5.0], ["2022", 10.0]], "pct") == [
        ("2022", pytest.approx(100.0))
    ]


def test_variacao_percentual_com_base_negativa_usa_o_modulo():
    assert variacoes([["2020", -10.0], ["2021", -5.0]], "pct") == [("2021", pytest.approx(50.0))]


def test_modo_invalido_e_recusado():
    with pytest.raises(ValueError, match="modo"):
        variacoes([["2020", 1.0], ["2021", 2.0]], "log")


def test_ponto_fora_de_3_sigma_e_acima_do_piso_e_suspeito():
    historico = [1.0, 1.2, 0.9, 1.1, 1.0, 0.8]
    assert classificar_ponto(15.0, historico, piso=10.0) == "suspeito"


def test_ponto_fora_de_3_sigma_mas_abaixo_do_piso_nao_e_suspeito():
    historico = [1.0, 1.2, 0.9, 1.1, 1.0, 0.8]
    assert (
        classificar_ponto(5.0, historico, piso=10.0) == "ok"
    )  # estatisticamente estranho, mas pequeno


def test_ponto_dentro_de_3_sigma_e_ok_mesmo_acima_do_piso():
    historico = [5.0, 25.0, -20.0, 30.0, -15.0, 10.0]  # série muito volátil
    assert classificar_ponto(12.0, historico, piso=10.0) == "ok"


def test_historico_curto_nao_trava():
    assert classificar_ponto(500.0, [1.0, 2.0], piso=10.0) == "ok"


# --- backtest nas séries reais ------------------------------------------------------------------


def test_backtest_sem_piso_marca_as_quebras_metodologicas_do_ibge(series_reais):
    """Documenta por que o piso existe: o 3σ puro reprova valores legítimos (Censo e Covid)."""
    pop = backtest(series_reais["TO-TER-01"], "pct", piso=0)
    assert (pop["avaliados"], [m["rotulo"] for m in pop["marcados"]]) == (
        18,
        ["2005", "2008", "2011"],
    )
    desoc = backtest(series_reais["TO-TER-07"], "abs", piso=0)
    assert (desoc["avaliados"], [m["rotulo"] for m in desoc["marcados"]]) == (
        54,
        ["1T2013", "1T2021", "3T2021"],
    )
    assert backtest(series_reais["TO-TER-03"], "pct", piso=0)["marcados"] == []


def test_backtest_com_a_politica_de_pisos_nao_marca_nenhum_ponto_real(series_reais):
    total = marcados = 0
    for fonte, (_ind, modo, piso) in POLITICA_3SIGMA.items():
        r = backtest(series_reais[fonte], modo, piso)
        total += r["avaliados"]
        marcados += len(r["marcados"])
    assert (total, marcados) == (90, 0)  # 0% de falso positivo (limite aprovado: 5%)


@pytest.mark.parametrize("fonte", ["TO-TER-01", "TO-TER-03", "TO-TER-07"])
def test_erro_grosseiro_de_dez_vezes_e_pego(series_reais, fonte):
    _ind, modo, piso = POLITICA_3SIGMA[fonte]
    serie = copy.deepcopy(series_reais[fonte])
    serie[-1][1] *= 10
    assert validacao.checar_serie(serie, modo, piso)["status"] == "suspeito"


@pytest.mark.parametrize("fonte", ["TO-TER-01", "TO-TER-03"])
def test_valor_dividido_por_dez_e_pego_nas_series_em_percentual(series_reais, fonte):
    _ind, modo, piso = POLITICA_3SIGMA[fonte]
    serie = copy.deepcopy(series_reais[fonte])
    serie[-1][1] /= 10
    assert validacao.checar_serie(serie, modo, piso)["status"] == "suspeito"


def test_limite_conhecido_desocupacao_dividida_por_dez_passa(series_reais):
    """Limite do piso de 6 p.p.: 4,1% -> 0,4% é uma queda de 3,7 p.p. e não é marcada. Piso menor que 5 marcaria
    também os pulos reais da Covid (1T2021 e 3T2021); a escolha está documentada na spec 35."""
    _ind, modo, piso = POLITICA_3SIGMA["TO-TER-07"]
    serie = copy.deepcopy(series_reais["TO-TER-07"])
    serie[-1][1] /= 10
    assert validacao.checar_serie(serie, modo, piso)["status"] == "ok"


def test_serie_com_menos_de_4_pontos_nao_e_avaliada():
    r = validacao.checar_serie([["2023", 1.0], ["2024", 2.0], ["2025", 50.0]], "pct", 10.0)
    assert r["status"] == "ok" and r["avaliado"] is False


def test_checar_serie_informa_o_ponto_suspeito(series_reais):
    serie = copy.deepcopy(series_reais["TO-TER-03"])
    serie[-1][1] *= 10
    r = validacao.checar_serie(serie, "pct", 10.0)
    assert r["rotulo"] == serie[-1][0] and r["variacao"] > 800 and r["avaliado"] is True


# --- cobertura (IBGE) ---------------------------------------------------------------------------


@pytest.mark.parametrize("fonte", IMPLEMENTADOS[:-1])
def test_ibge_completo_passa(registros, fonte):
    validar_cobertura_ibge(fonte, registros[fonte])


def test_ibge_com_138_municipios_em_um_periodo_e_recusado(registros):
    rec = [
        r
        for r in registros["TO-TER-02"]
        if not (r["id_municipio"] == "1721000" and r["periodo_ref"].startswith("2023"))
    ]
    with pytest.raises(ColetaRecusada, match="138") as e:
        validar_cobertura_ibge("TO-TER-02", rec)
    assert e.value.suspeito is False


def test_ibge_municipio_fora_dos_139_e_recusado(registros):
    rec = copy.deepcopy(registros["TO-TER-04"])
    rec[0]["id_municipio"] = "9999999"
    with pytest.raises(ColetaRecusada, match="9999999"):
        validar_cobertura_ibge("TO-TER-04", rec)


def test_ibge_registro_duplicado_e_recusado(registros):
    rec = registros["TO-TER-04"] + [copy.deepcopy(registros["TO-TER-04"][0])]
    with pytest.raises(ColetaRecusada, match="duplicad"):
        validar_cobertura_ibge("TO-TER-04", rec)


@pytest.mark.parametrize("valor", [None, math.nan, math.inf, True, "12"])
def test_ibge_valor_que_nao_e_numero_finito_e_recusado(registros, valor):
    rec = copy.deepcopy(registros["TO-TER-04"])
    rec[3]["valor_num"] = valor
    with pytest.raises(ColetaRecusada, match="número"):
        validar_cobertura_ibge("TO-TER-04", rec)


def test_ibge_vazio_e_recusado():
    with pytest.raises(ColetaRecusada, match="nenhum registro"):
        validar_cobertura_ibge("TO-TER-04", [])


def test_ibge_estadual_exige_um_registro_por_periodo(registros):
    validar_cobertura_ibge("TO-TER-03", registros["TO-TER-03"])
    rec = registros["TO-TER-03"] + [copy.deepcopy(registros["TO-TER-03"][0])]
    with pytest.raises(ColetaRecusada, match="duplicad"):
        validar_cobertura_ibge("TO-TER-03", rec)


# --- SICONFI ------------------------------------------------------------------------------------


def test_rcl_com_estado_passa_mesmo_com_poucos_municipios(registros):
    validar_rcl(registros["TO-REC-02"])  # a fixture tem só 3 municípios: os demais atrasaram


def test_rcl_sem_o_estado_no_exercicio_e_recusada(registros):
    rec = [
        r
        for r in registros["TO-REC-02"]
        if not (r["id_municipio"] is None and r["periodo_ref"].startswith("2025"))
    ]
    with pytest.raises(ColetaRecusada, match=r"estado.*2025"):
        validar_rcl(rec)


def test_rcl_municipio_fora_dos_139_e_recusado(registros):
    rec = copy.deepcopy(registros["TO-REC-02"])
    municipal = next(r for r in rec if r["id_municipio"])
    municipal["id_municipio"] = "1234567"
    with pytest.raises(ColetaRecusada, match="1234567"):
        validar_rcl(rec)


@pytest.mark.parametrize("valor", [0, -5.0, math.nan, None, True])
def test_rcl_valor_invalido_e_recusado(registros, valor):
    rec = copy.deepcopy(registros["TO-REC-02"])
    rec[0]["valor_num"] = valor
    with pytest.raises(ColetaRecusada):
        validar_rcl(rec)


def test_rcl_vazia_e_recusada():
    with pytest.raises(ColetaRecusada, match="nenhum registro"):
        validar_rcl([])


# --- validar_fonte (despacho) -------------------------------------------------------------------


def _hist(series_reais):
    return lambda fonte: copy.deepcopy(series_reais[fonte])


def test_validar_fonte_aceita_os_dados_reais_gravados(registros, series_reais):
    for fonte in FONTES:
        validar_fonte(fonte, registros[fonte], _hist(series_reais))


def test_pib_estadual_dez_vezes_maior_e_suspeito_e_marcado_como_tal(registros, series_reais):
    rec = copy.deepcopy(registros["TO-TER-03"])
    for r in rec:
        if r["periodo_ref"].startswith("2023"):
            r["valor_num"] *= 10
    with pytest.raises(ColetaRecusada, match="3σ") as e:
        validar_fonte("TO-TER-03", rec, _hist(series_reais))
    assert e.value.suspeito is True


def test_populacao_estadual_pela_soma_dos_municipios_tambem_e_checada(registros, series_reais):
    rec = copy.deepcopy(registros["TO-TER-01"])
    for r in rec:
        if r["periodo_ref"].startswith("2026"):
            r["valor_num"] *= 10  # soma dos 139 municípios fica 10x
    with pytest.raises(ColetaRecusada, match="3σ"):
        validar_fonte("TO-TER-01", rec, _hist(series_reais))


def test_municipal_volatil_so_tem_integridade_nao_3_sigma(registros, series_reais):
    """Um município que triplica a produção agrícola é notícia, não erro: PAM não passa pelo 3σ."""
    rec = copy.deepcopy(registros["TO-TER-05"])
    rec[0]["valor_num"] *= 50
    validar_fonte("TO-TER-05", rec, lambda f: pytest.fail("PAM não usa histórico"))


def test_historico_indisponivel_falha_com_a_fonte_nao_aceita_em_silencio(registros):
    def sem_historico(fonte):
        raise OSError("API fora do ar")

    with pytest.raises(OSError, match="fora do ar"):
        validar_fonte("TO-TER-03", registros["TO-TER-03"], sem_historico)


def test_titulares_com_menos_de_139_prefeitos_e_recusado(registros):
    rec = [r for r in registros[TITULARES] if r["id_municipio"] != "1721000"]
    with pytest.raises(ColetaRecusada, match=r"139|Palmas|1721000|cobertura"):
        validar_fonte(TITULARES, rec, lambda f: None)


def test_titulares_completos_passam(registros):
    validar_fonte(TITULARES, registros[TITULARES], lambda f: None)


def test_politica_so_cobre_estaduais_e_estruturais():
    assert set(POLITICA_3SIGMA) == {"TO-TER-01", "TO-TER-03", "TO-TER-07"}
    assert POLITICA_3SIGMA["TO-TER-07"][1] == "abs"  # taxa: diferença em pontos percentuais
    assert {p[1] for f, p in POLITICA_3SIGMA.items() if f != "TO-TER-07"} == {"pct"}


# --- checar_novos: toda variação que termina num período recém-coletado --------------------------


def test_checar_novos_pega_a_emenda_quando_a_janela_inteira_vem_multiplicada():
    from src.orquestracao.validacao import checar_novos

    historico = [[str(2000 + i), 100.0 + 2 * i] for i in range(10)]  # +2% a.a. aproximado
    janela = [["2010", 1120.0], ["2011", 1140.0], ["2012", 1160.0]]  # tudo x10 a partir de 2010
    r = checar_novos([*historico, *janela], {"2010", "2011", "2012"}, "pct", 10.0)
    assert r["status"] == "suspeito" and r["rotulo"] == "2010"


def test_checar_novos_ignora_variacoes_antigas_e_aceita_serie_normal():
    from src.orquestracao.validacao import checar_novos

    serie = [["2000", 100.0], ["2001", 300.0], *[[str(2002 + i), 300.0 + i] for i in range(8)]]
    assert (
        checar_novos(serie, {"2008", "2009"}, "pct", 10.0)["status"] == "ok"
    )  # o salto de 2001 é velho
