"""
painel_dados.json: mesclar o SICONFI por município e consolidar o arquivo (Task 35, passo 6).
Regra do SICONFI (decisão do Bruno): o atraso de municípios não impede a atualização; quem já tinha valor
nunca perde (piso); ausente continua ausente, nunca zero.
"""

import copy

import pytest
from src.orquestracao.fontes import FONTES, IMPLEMENTADOS, TITULARES
from src.orquestracao.painel import consolidar, instanciar, mesclar_indicador, mesclar_serie

IND = "receita_corrente_liquida"
T0 = "2026-10-21T17:00:00Z"
T1 = "2026-11-22T17:00:00Z"


# --- mesclar_serie ------------------------------------------------------------------------------


def test_mesclar_serie_une_por_ano_e_o_novo_prevalece():
    antiga = [["2023", 1.0], ["2024", 2.0], ["2025", 3.0]]
    nova = [["2024", 20.0], ["2025", 30.0], ["2026", 40.0]]
    assert mesclar_serie(antiga, nova) == [
        ["2023", 1.0],
        ["2024", 20.0],
        ["2025", 30.0],
        ["2026", 40.0],
    ]


def test_mesclar_serie_sem_lado_devolve_o_outro_e_nao_altera_as_entradas():
    antiga, nova = [["2024", 2.0]], [["2025", 3.0]]
    copia = copy.deepcopy((antiga, nova))
    assert mesclar_serie(antiga, []) == antiga and mesclar_serie([], nova) == nova
    mesclar_serie(antiga, nova)
    assert (antiga, nova) == copia


def test_mesclar_serie_ordena_por_ano():
    assert mesclar_serie([["2025", 3.0]], [["2023", 1.0]]) == [["2023", 1.0], ["2025", 3.0]]


@pytest.mark.parametrize("rotulo", ["1T2026", "2026-01", "26", ""])
def test_mesclar_serie_so_aceita_rotulo_anual(rotulo):
    with pytest.raises(ValueError, match="anual"):
        mesclar_serie([[rotulo, 1.0]], [])


# --- mesclar_indicador (SICONFI) ----------------------------------------------------------------


def _painel(municipios: dict, estado: list | None = None, unidade: str = "R$ mil"):
    return {
        "unidades": {IND: unidade},
        "estado": {IND: estado} if estado else {},
        "municipios": {m: {IND: s} for m, s in municipios.items()},
    }


def test_municipio_atrasado_mantem_o_valor_anterior_e_o_novo_entra():
    anterior = _painel(
        {
            "A": [["2023", 1.0], ["2024", 2.0], ["2025", 3.0]],
            "B": [["2023", 10.0], ["2024", 20.0], ["2025", 30.0]],
        },
        estado=[["2023", 100.0], ["2024", 200.0], ["2025", 300.0]],
    )
    novo = _painel(
        {
            "A": [["2024", 2.5], ["2025", 3.5], ["2026", 4.0]],
            "C": [["2026", 7.0]],
        },  # B atrasou; C é novo
        estado=[["2025", 310.0], ["2026", 400.0]],
    )
    mesclar_indicador(novo, anterior, IND)
    m = novo["municipios"]
    assert m["A"][IND] == [
        ["2023", 1.0],
        ["2024", 2.5],
        ["2025", 3.5],
        ["2026", 4.0],
    ]  # retificação entrou
    assert m["B"][IND] == [
        ["2023", 10.0],
        ["2024", 20.0],
        ["2025", 30.0],
    ]  # atrasado: piso preservado
    assert m["C"][IND] == [["2026", 7.0]]
    assert novo["estado"][IND] == [
        ["2023", 100.0],
        ["2024", 200.0],
        ["2025", 310.0],
        ["2026", 400.0],
    ]
    assert novo["unidades"][IND] == "R$ mil"


def test_piso_a_cobertura_por_exercicio_nunca_diminui():
    anterior = _painel(
        {f"M{i}": [["2024", 1.0], ["2025", 2.0]] for i in range(10)},
        estado=[["2024", 1.0], ["2025", 2.0]],
    )
    novo = _painel(
        {f"M{i}": [["2025", 2.5]] for i in range(3)}, estado=[["2025", 2.5]]
    )  # só 3 de 10 entregaram
    mesclar_indicador(novo, anterior, IND)

    def cobertura(p, ano):
        return sum(1 for s in p["municipios"].values() if any(r == ano for r, _ in s.get(IND, [])))

    for ano in ("2024", "2025"):
        assert cobertura(novo, ano) >= cobertura(anterior, ano)


def test_municipio_ausente_continua_ausente_e_nunca_vira_zero():
    anterior = _painel({"A": [["2025", 3.0]]})
    novo = _painel({"B": [["2025", 4.0]]})
    mesclar_indicador(novo, anterior, IND)
    assert "A" in novo["municipios"] and "C" not in novo["municipios"]
    valores = [v for m in novo["municipios"].values() for _, v in m[IND]]
    assert 0 not in valores


def test_sem_painel_anterior_o_novo_fica_como_esta():
    novo = _painel({"A": [["2025", 3.0]]}, estado=[["2025", 9.0]])
    mesclar_indicador(novo, {"unidades": {}, "estado": {}, "municipios": {}}, IND)
    assert novo["municipios"]["A"][IND] == [["2025", 3.0]] and novo["estado"][IND] == [
        ["2025", 9.0]
    ]


# --- consolidar ---------------------------------------------------------------------------------


@pytest.fixture
def registros(rede_gravada):
    """Registros reais das 9 fontes, a partir das respostas gravadas."""
    saida = {}
    for f in FONTES:
        c = instanciar(f)
        saida[f] = c.transformar(c.extrair())
    return saida


@pytest.fixture(autouse=True)
def _ano_do_siconfi(monkeypatch):
    from datetime import UTC, datetime

    from src.coletores import siconfi

    class Agora(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 14, tzinfo=UTC)

    monkeypatch.setattr(siconfi, "datetime", Agora)


def test_consolidar_tudo_gera_o_arquivo_completo(registros):
    p = consolidar(None, registros, T0)
    assert p["gerado_em"] == T0 and list(p["fontes"]) == FONTES
    assert all(m["status"] == "ok" and m["coletado_em"] == T0 for m in p["fontes"].values())
    assert len(p["municipios"]) == 139 and p["titulares"]["estado"]["nome"] == "WANDERLEI BARBOSA"


def test_consolidar_uma_fonte_so_troca_o_que_e_dela(registros):
    antes = consolidar(None, registros, T0)
    novos = copy.deepcopy(registros["TO-TER-04"])
    for r in novos:
        r["valor_num"] = r["valor_num"] + 1000  # a área "mudou"
    depois = consolidar(antes, {"TO-TER-04": novos}, T1)
    assert depois["gerado_em"] == T1
    assert depois["fontes"]["TO-TER-04"]["coletado_em"] == T1
    for f in FONTES:
        if f != "TO-TER-04":
            assert depois["fontes"][f] == antes["fontes"][f], f  # as outras mantêm o carimbo antigo
    assert (
        depois["municipios"]["1721000"]["area_territorial"]
        != antes["municipios"]["1721000"]["area_territorial"]
    )
    outros = {k: v for k, v in antes["municipios"]["1721000"].items() if k != "area_territorial"}
    assert {
        k: v for k, v in depois["municipios"]["1721000"].items() if k != "area_territorial"
    } == outros
    assert depois["titulares"] == antes["titulares"]
    assert depois["estado"]["populacao_residente"] == antes["estado"]["populacao_residente"]


def test_consolidar_sem_nada_novo_mantem_os_dados(registros):
    antes = consolidar(None, registros, T0)
    depois = consolidar(antes, {}, T1)
    assert {k: v for k, v in depois.items() if k != "gerado_em"} == {
        k: v for k, v in antes.items() if k != "gerado_em"
    }


def test_consolidar_siconfi_preserva_o_municipio_atrasado(registros):
    antes = consolidar(None, registros, T0)
    # nova coleta do SICONFI sem Abreulândia (atrasou): ela mantém o valor que já tinha
    novos = [r for r in registros["TO-REC-02"] if r["id_municipio"] != "1700251"]
    depois = consolidar(antes, {"TO-REC-02": novos}, T1)
    assert depois["municipios"]["1700251"][IND] == antes["municipios"]["1700251"][IND]
    assert depois["estado"][IND] == antes["estado"][IND]
    assert depois["fontes"]["TO-REC-02"]["registros"] == len(novos)


def test_consolidar_fonte_falha_e_sem_dado_anterior_marca_erro(registros):
    parcial = consolidar(None, {f: r for f, r in registros.items() if f != "TO-TER-05"}, T0)
    assert parcial["fontes"]["TO-TER-05"]["status"] == "erro"
    assert "producao_agricola" not in parcial["estado"]


def test_consolidar_titulares_so_mudam_quando_aceitos(registros):
    antes = consolidar(None, registros, T0)
    novos = copy.deepcopy(registros[TITULARES])
    novos[0]["nome_titular"] = "OUTRO NOME"
    depois = consolidar(antes, {TITULARES: novos}, T1)
    assert any(
        t["nome"] == "OUTRO NOME"
        for t in [*depois["titulares"]["municipios"].values(), depois["titulares"]["estado"]]
    )
    assert depois["fontes"][TITULARES]["coletado_em"] == T1
    assert all(depois["fontes"][f] == antes["fontes"][f] for f in IMPLEMENTADOS)
