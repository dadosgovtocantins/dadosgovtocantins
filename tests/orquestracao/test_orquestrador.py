"""Cenários da orquestração (Task 35, passo 7): sentinela, coleta, validação e o que é publicado.
Tudo com as respostas reais gravadas e sentinelas falsas; nenhuma rede."""

import copy
from datetime import UTC, datetime, timedelta

import pytest
from src.orquestracao.estado import estado_vazio, para_iso, validar
from src.orquestracao.fontes import FONTES, TITULARES
from src.orquestracao.orquestrador import executar
from src.orquestracao.painel import consolidar, instanciar
from src.orquestracao.sentinelas import Sentinela, SentinelaError

T0 = datetime(2026, 10, 21, 17, 0, tzinfo=UTC)
T1 = T0 + timedelta(days=1)


class SentinelasFalsas:
    def __init__(self, marcas=None, falham=()):
        self.marcas, self.falham, self.consultas = marcas or {}, set(falham), []

    def consultar(self, id_fonte):
        self.consultas.append(id_fonte)
        if id_fonte in self.falham:
            raise SentinelaError(f"{id_fonte}: sentinela falhou: sem rede")
        return Sentinela(marca=self.marcas.get(id_fonte, f"m-{id_fonte}"), ultimo_periodo="2025")


@pytest.fixture(autouse=True)
def _ano_do_siconfi(monkeypatch):
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


@pytest.fixture
def historicos(rede_gravada):
    from src.orquestracao.historico import historico_estadual

    return historico_estadual


def _coletar(registros, falham=()):
    chamadas = []

    def coletar(id_fonte):
        chamadas.append(id_fonte)
        if id_fonte in falham:
            raise OSError("API fora do ar")
        return copy.deepcopy(registros[id_fonte])

    coletar.chamadas = chamadas
    return coletar


def _primeira(registros, historicos, **kw):
    """Primeira execução: nada coletado ainda, tudo é novidade."""
    return executar(
        estado=estado_vazio(T0),
        painel_anterior=None,
        agora=T0,
        forcar=[],
        sentinelas=kw.pop("sentinelas", SentinelasFalsas()),
        coletar=kw.pop("coletar", _coletar(registros)),
        historico=historicos,
    )


def _depois(res, registros, historicos, agora=T1, **kw):
    return executar(
        estado=res.estado,
        painel_anterior=res.painel,
        agora=agora,
        forcar=kw.pop("forcar", []),
        sentinelas=kw.pop("sentinelas", SentinelasFalsas()),
        coletar=kw.pop("coletar", _coletar(registros)),
        historico=historicos,
    )


def test_primeira_execucao_coleta_as_9_fontes_e_estado_fica_valido(registros, historicos):
    res = _primeira(registros, historicos)
    assert res.aceitas == FONTES and res.painel is not None
    validar(res.estado)
    assert all(
        f["status"] == "ok" and f["coletado_em"] == para_iso(T0)
        for f in res.estado["fontes"].values()
    )
    assert res.estado["fontes"]["TO-TER-01"]["marca_sentinela"] == "m-TO-TER-01"


def test_a_sem_novidade_nao_coleta_e_so_confirma(registros, historicos):
    res = _primeira(registros, historicos)
    coletar = _coletar(registros)
    seg = _depois(res, registros, historicos, coletar=coletar)
    assert coletar.chamadas == [] and seg.painel is None and seg.aceitas == []
    for id_fonte, f in seg.estado["fontes"].items():
        assert f["verificado_em"] == f["confirmado_em"] == para_iso(T1)
        assert f["coletado_em"] == para_iso(T0), id_fonte
        assert seg.relatorio[id_fonte] == "sem novidade"


def test_b_novidade_coleta_so_aquela_fonte_e_atualiza_os_dois_arquivos(registros, historicos):
    res = _primeira(registros, historicos)
    coletar = _coletar(registros)
    seg = _depois(
        res,
        registros,
        historicos,
        coletar=coletar,
        sentinelas=SentinelasFalsas({"TO-TER-04": "nova"}),
    )
    assert coletar.chamadas == ["TO-TER-04"] and seg.aceitas == ["TO-TER-04"]
    f = seg.estado["fontes"]["TO-TER-04"]
    assert f["marca_sentinela"] == "nova" and f["coletado_em"] == para_iso(T1)
    assert seg.estado["fontes"]["TO-TER-01"]["coletado_em"] == para_iso(T0)
    assert seg.painel["fontes"]["TO-TER-04"]["coletado_em"] == para_iso(T1)


def test_c_falha_mantem_o_dado_anterior_e_conta_a_falha(registros, historicos):
    res = _primeira(registros, historicos)
    sent = SentinelasFalsas({"TO-TER-05": "nova"})
    seg = _depois(
        res, registros, historicos, sentinelas=sent, coletar=_coletar(registros, ["TO-TER-05"])
    )
    f = seg.estado["fontes"]["TO-TER-05"]
    assert (f["status"], f["falhas_consecutivas"]) == ("erro", 1) and "OSError" in f[
        "mensagem_erro"
    ]
    assert f["marca_sentinela"] == "m-TO-TER-05" and f["coletado_em"] == para_iso(
        T0
    )  # marca antiga: tenta de novo
    assert seg.painel is None  # nada aceito: o painel não muda
    terceira = _depois(
        seg,
        registros,
        historicos,
        agora=T1 + timedelta(days=1),
        sentinelas=sent,
        coletar=_coletar(registros, ["TO-TER-05"]),
    )
    assert terceira.estado["fontes"]["TO-TER-05"]["falhas_consecutivas"] == 2
    ok = _depois(terceira, registros, historicos, agora=T1 + timedelta(days=2), sentinelas=sent)
    f = ok.estado["fontes"]["TO-TER-05"]
    assert (f["status"], f["falhas_consecutivas"], f["mensagem_erro"]) == ("ok", 0, None)


def test_falha_de_uma_fonte_nao_derruba_as_outras(registros, historicos):
    sent = SentinelasFalsas()
    res = _primeira(
        registros, historicos, sentinelas=sent, coletar=_coletar(registros, ["TO-TER-02"])
    )
    assert "TO-TER-02" not in res.aceitas and len(res.aceitas) == 8
    assert res.estado["fontes"]["TO-TER-02"]["status"] == "erro"
    assert (
        res.painel["fontes"]["TO-TER-02"]["status"] == "erro"
    )  # sem dado anterior: "Não coletado"


def test_d_agregado_estadual_suspeito_nao_e_publicado(registros, historicos):
    res = _primeira(registros, historicos)
    ruim = copy.deepcopy(registros)
    for r in ruim["TO-TER-03"]:
        r["valor_num"] *= 10  # PIB estadual multiplicado por 10
    seg = _depois(
        res,
        registros,
        historicos,
        sentinelas=SentinelasFalsas({"TO-TER-03": "nova"}),
        coletar=_coletar(ruim),
    )
    f = seg.estado["fontes"]["TO-TER-03"]
    assert (
        f["status"] == "suspeito" and "3σ" in f["mensagem_erro"] and f["falhas_consecutivas"] == 1
    )
    assert seg.aceitas == [] and seg.painel is None


def test_f_ibge_com_menos_de_139_recusa_a_fonte_inteira(registros, historicos):
    res = _primeira(registros, historicos)
    curto = copy.deepcopy(registros)
    curto["TO-TER-05"] = curto["TO-TER-05"][:-1]
    seg = _depois(
        res,
        registros,
        historicos,
        sentinelas=SentinelasFalsas({"TO-TER-05": "nova"}),
        coletar=_coletar(curto),
    )
    assert seg.estado["fontes"]["TO-TER-05"]["status"] == "erro" and seg.aceitas == []


def test_g_siconfi_com_municipio_atrasado_atualiza_e_preserva_o_piso(registros, historicos):
    res = _primeira(registros, historicos)
    ind = "receita_corrente_liquida"
    antes = res.painel["municipios"]["1700251"][ind]
    novos = copy.deepcopy(registros)
    novos["TO-REC-02"] = [r for r in novos["TO-REC-02"] if r["id_municipio"] != "1700251"]
    seg = _depois(
        res,
        registros,
        historicos,
        sentinelas=SentinelasFalsas({"TO-REC-02": "nova"}),
        coletar=_coletar(novos),
    )
    assert seg.aceitas == ["TO-REC-02"] and seg.estado["fontes"]["TO-REC-02"]["status"] == "ok"
    assert seg.painel["municipios"]["1700251"][ind] == antes


def test_sentinela_falha_marca_erro_sem_coletar(registros, historicos):
    res = _primeira(registros, historicos)
    coletar = _coletar(registros)
    seg = _depois(
        res,
        registros,
        historicos,
        coletar=coletar,
        sentinelas=SentinelasFalsas(falham=["TO-TER-01"]),
    )
    f = seg.estado["fontes"]["TO-TER-01"]
    assert (
        f["status"] == "erro"
        and f["falhas_consecutivas"] == 1
        and "TO-TER-01" not in coletar.chamadas
    )
    assert f["verificado_em"] == para_iso(T0)  # não foi verificada hoje
    assert seg.estado["fontes"]["TO-TER-02"]["status"] == "ok"  # as outras seguem


def test_forcar_coleta_mesmo_sem_novidade_e_mesmo_com_a_sentinela_fora(registros, historicos):
    res = _primeira(registros, historicos)
    coletar = _coletar(registros)
    seg = _depois(
        res,
        registros,
        historicos,
        coletar=coletar,
        forcar=["TO-TER-06", "TO-TER-04"],
        sentinelas=SentinelasFalsas(falham=["TO-TER-04"]),
    )
    assert sorted(coletar.chamadas) == ["TO-TER-04", "TO-TER-06"]
    f4 = seg.estado["fontes"]["TO-TER-04"]
    assert f4["status"] == "ok" and f4["marca_sentinela"] == "m-TO-TER-04"  # marca antiga mantida


@pytest.mark.parametrize(("fonte", "dias"), [("TO-REC-02", 30), (TITULARES, 30)])
def test_recoleta_fixa_de_30_dias_mesmo_sem_novidade(registros, historicos, fonte, dias):
    res = _primeira(registros, historicos)
    antes = _coletar(registros)
    _depois(res, registros, historicos, agora=T0 + timedelta(days=dias - 1), coletar=antes)
    assert fonte not in antes.chamadas
    depois = _coletar(registros)
    _depois(res, registros, historicos, agora=T0 + timedelta(days=dias), coletar=depois)
    assert fonte in depois.chamadas
    assert [f for f in depois.chamadas if f not in ("TO-REC-02", TITULARES)] == []


@pytest.mark.parametrize(
    ("fonte", "dias"), [("TO-TER-01", 450), ("TO-TER-07", 150), ("TO-REC-02", 60)]
)
def test_defasado_depois_do_prazo_sem_confirmacao(registros, historicos, fonte, dias):
    res = _primeira(registros, historicos)
    sent = SentinelasFalsas(falham=[fonte])  # a sentinela some: a fonte não é mais confirmada
    no_prazo = _depois(res, registros, historicos, agora=T0 + timedelta(days=dias), sentinelas=sent)
    assert no_prazo.estado["fontes"][fonte]["status"] == "erro"
    vencida = _depois(
        res, registros, historicos, agora=T0 + timedelta(days=dias, minutes=1), sentinelas=sent
    )
    assert vencida.estado["fontes"][fonte]["status"] == "defasado"
    assert vencida.estado["fontes"][fonte]["mensagem_erro"]  # o motivo não se perde
    validar(vencida.estado)


def test_fonte_confirmada_todo_dia_nunca_fica_defasada(registros, historicos):
    res = _primeira(registros, historicos)
    seg = _depois(res, registros, historicos, agora=T0 + timedelta(days=600))
    assert seg.estado["fontes"]["TO-TER-01"]["status"] == "ok"


def test_entradas_nao_sao_alteradas(registros, historicos):
    res = _primeira(registros, historicos)
    estado, painel = copy.deepcopy(res.estado), copy.deepcopy(res.painel)
    _depois(res, registros, historicos, forcar=FONTES)
    assert (res.estado, res.painel) == (estado, painel)


def test_painel_sem_coleta_aceita_e_none_e_consolidar_nao_e_chamado(
    registros, historicos, monkeypatch
):
    res = _primeira(registros, historicos)
    monkeypatch.setattr(
        "src.orquestracao.orquestrador.consolidar", lambda *a: pytest.fail("não deveria")
    )
    assert _depois(res, registros, historicos).painel is None


def test_consolidar_continua_a_ser_o_formato_do_painel(registros, historicos):
    res = _primeira(registros, historicos)
    assert res.painel == consolidar(None, registros, para_iso(T0))
