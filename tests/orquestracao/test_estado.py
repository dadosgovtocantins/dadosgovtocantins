"""
estado_fontes.json (Task 35, passo 3): schema validado, escrita atômica e catálogo das 9 fontes.
"""

import copy
import json
from pathlib import Path

import pytest
from src.orquestracao import estado
from src.orquestracao.fontes import (
    FONTES,
    IMPLEMENTADOS,
    PERIODICIDADE,
    PRAZO_DEFASADO_DIAS,
    RECOLETA_FIXA_DIAS,
    TITULARES,
)

RAIZ = Path(__file__).parents[2]
AGORA = "2026-10-21T17:00:12Z"


def _fonte(**extra):
    base = {
        "ultimo_periodo_coletado": "2025",
        "marca_sentinela": "2025|2026-09-30",
        "verificado_em": AGORA,
        "coletado_em": "2026-10-15T03:00:00Z",
        "confirmado_em": AGORA,
        "status": "ok",
        "falhas_consecutivas": 0,
        "mensagem_erro": None,
        "proxima_divulgacao": "2027-08-28",
    }
    return {**base, **extra}


def _estado():
    return {
        "versao": 1,
        "ultima_execucao_orquestrador": AGORA,
        "fontes": {f: _fonte() for f in FONTES},
    }


# --- catálogo ---------------------------------------------------------------------------------


def test_catalogo_tem_as_9_fontes_atuais():
    assert len(FONTES) == 9 and len(set(FONTES)) == 9
    assert IMPLEMENTADOS == [f"TO-TER-0{i}" for i in range(1, 8)] + ["TO-REC-02"]
    assert TITULARES == "TO-GER-01" and FONTES == [*IMPLEMENTADOS, TITULARES]


def test_cada_fonte_tem_periodicidade_e_prazo_de_defasagem():
    assert set(PERIODICIDADE) == set(FONTES)
    assert PERIODICIDADE["TO-TER-07"] == "trimestral"
    assert PERIODICIDADE["TO-REC-02"] == PERIODICIDADE["TO-GER-01"] == "mensal"
    assert PRAZO_DEFASADO_DIAS == {
        "anual": 450,
        "trimestral": 150,
        "mensal": 60,
    }  # decisão do Bruno
    assert RECOLETA_FIXA_DIAS == {"TO-REC-02": 30, "TO-GER-01": 30}


# --- schema -----------------------------------------------------------------------------------


def test_estado_valido_passa():
    estado.validar(_estado())


def test_estado_vazio_e_valido_e_tem_todas_as_fontes():
    vazio = estado.estado_vazio()
    estado.validar(vazio)
    assert set(vazio["fontes"]) == set(FONTES)
    assert all(
        f["marca_sentinela"] is None and f["falhas_consecutivas"] == 0
        for f in vazio["fontes"].values()
    )


def _sem(chave, d):
    d = copy.deepcopy(d)
    del d[chave]
    return d


INVALIDOS = {
    "fonte faltando": lambda e: e["fontes"].pop("TO-TER-01"),
    "fonte desconhecida": lambda e: e["fontes"].update({"TO-XXX-99": _fonte()}),
    "chave desconhecida no topo": lambda e: e.update({"extra": 1}),
    "chave desconhecida na fonte": lambda e: e["fontes"]["TO-TER-01"].update({"extra": 1}),
    "campo faltando na fonte": lambda e: e["fontes"]["TO-TER-01"].pop("coletado_em"),
    "versão errada": lambda e: e.update({"versao": 2}),
    "status fora do enum": lambda e: e["fontes"]["TO-TER-01"].update({"status": "quebrado"}),
    "status nulo": lambda e: e["fontes"]["TO-TER-01"].update({"status": None}),
    "falhas como bool": lambda e: e["fontes"]["TO-TER-01"].update({"falhas_consecutivas": True}),
    "falhas negativas": lambda e: e["fontes"]["TO-TER-01"].update({"falhas_consecutivas": -1}),
    "falhas como texto": lambda e: e["fontes"]["TO-TER-01"].update({"falhas_consecutivas": "2"}),
    "data com fuso": lambda e: e["fontes"]["TO-TER-01"].update(
        {"verificado_em": "2026-10-21T14:00:12-03:00"}
    ),
    "data sem hora": lambda e: e["fontes"]["TO-TER-01"].update({"coletado_em": "2026-10-21"}),
    "data inexistente": lambda e: e["fontes"]["TO-TER-01"].update(
        {"coletado_em": "2026-02-30T00:00:00Z"}
    ),
    "execução em formato errado": lambda e: e.update({"ultima_execucao_orquestrador": "ontem"}),
    "próxima divulgação com hora": lambda e: e["fontes"]["TO-TER-01"].update(
        {"proxima_divulgacao": "2027-08-28T00:00:00Z"}
    ),
    "próxima divulgação inexistente": lambda e: e["fontes"]["TO-TER-01"].update(
        {"proxima_divulgacao": "2027-13-01"}
    ),
    "mensagem com quebra de linha": lambda e: e["fontes"]["TO-TER-01"].update(
        {"mensagem_erro": "a\nb"}
    ),
    "mensagem enorme": lambda e: e["fontes"]["TO-TER-01"].update({"mensagem_erro": "x" * 301}),
    "período vazio": lambda e: e["fontes"]["TO-TER-01"].update({"ultimo_periodo_coletado": ""}),
    "marca como número": lambda e: e["fontes"]["TO-TER-01"].update({"marca_sentinela": 7}),
}


@pytest.mark.parametrize("caso", list(INVALIDOS))
def test_estado_invalido_e_recusado(caso):
    e = _estado()
    INVALIDOS[caso](e)
    with pytest.raises(estado.EstadoInvalidoError):
        estado.validar(e)


def test_estado_que_nao_e_objeto_e_recusado():
    for lixo in (None, [], "texto", 3):
        with pytest.raises(estado.EstadoInvalidoError):
            estado.validar(lixo)


def test_campos_opcionais_aceitam_nulo():
    e = _estado()
    e["fontes"]["TO-TER-01"].update(
        {
            k: None
            for k in (
                "ultimo_periodo_coletado",
                "marca_sentinela",
                "verificado_em",
                "coletado_em",
                "confirmado_em",
                "mensagem_erro",
                "proxima_divulgacao",
            )
        }
    )
    estado.validar(e)


# --- datas ------------------------------------------------------------------------------------


def test_iso_utc_e_leitura_de_volta():
    from datetime import UTC, datetime

    dt = datetime(2026, 10, 21, 17, 0, 12, 345678, tzinfo=UTC)
    assert estado.para_iso(dt) == "2026-10-21T17:00:12Z"  # sem fração
    assert estado.de_iso("2026-10-21T17:00:12Z") == datetime(2026, 10, 21, 17, 0, 12, tzinfo=UTC)
    assert estado.de_iso(None) is None


def test_para_iso_converte_fuso_para_utc():
    from datetime import datetime, timedelta, timezone

    brasilia = datetime(2026, 10, 21, 14, 0, 0, tzinfo=timezone(timedelta(hours=-3)))
    assert estado.para_iso(brasilia) == "2026-10-21T17:00:00Z"
    with pytest.raises(ValueError, match="fuso"):
        estado.para_iso(datetime(2026, 10, 21, 14, 0, 0))  # sem fuso: ambíguo, recusado


# --- leitura e escrita atômica ----------------------------------------------------------------


def test_gravar_e_ler_dao_o_mesmo_estado(tmp_path):
    caminho = tmp_path / "estado_fontes.json"
    e = _estado()
    estado.gravar(caminho, e)
    assert estado.ler(caminho) == e
    texto = caminho.read_text("utf-8")
    assert texto.endswith("}\n") and '"versao": 1' in texto
    assert list(json.loads(texto)["fontes"]) == FONTES  # ordem estável: diff do Git legível


def test_gravar_estado_invalido_nao_toca_no_arquivo(tmp_path):
    caminho = tmp_path / "estado_fontes.json"
    estado.gravar(caminho, _estado())
    antes = caminho.read_bytes()
    ruim = _estado()
    ruim["fontes"]["TO-TER-01"]["status"] = "quebrado"
    with pytest.raises(estado.EstadoInvalidoError):
        estado.gravar(caminho, ruim)
    assert caminho.read_bytes() == antes and not list(tmp_path.glob("*.tmp"))


def test_queda_no_meio_da_gravacao_preserva_o_original_e_limpa_o_temporario(tmp_path, monkeypatch):
    caminho = tmp_path / "estado_fontes.json"
    estado.gravar(caminho, _estado())
    antes = caminho.read_bytes()

    def falha(self, alvo):
        raise OSError("disco cheio")

    monkeypatch.setattr(Path, "replace", falha)
    novo = _estado()
    novo["ultima_execucao_orquestrador"] = "2026-10-22T17:00:00Z"
    with pytest.raises(OSError, match="disco cheio"):
        estado.gravar(caminho, novo)
    assert caminho.read_bytes() == antes and not list(tmp_path.glob("*.tmp"))


def test_ler_arquivo_corrompido_ou_inexistente_da_erro_claro(tmp_path):
    with pytest.raises(estado.EstadoInvalidoError, match="não existe"):
        estado.ler(tmp_path / "nada.json")
    ruim = tmp_path / "ruim.json"
    ruim.write_text("{não é json", "utf-8")
    with pytest.raises(estado.EstadoInvalidoError, match="JSON"):
        estado.ler(ruim)


def test_arquivo_versionado_do_repositorio_e_valido():
    caminho = RAIZ / "src" / "ui" / "data" / "estado_fontes.json"
    if not caminho.exists():
        pytest.skip("estado_fontes.json ainda não foi criado (passo --inicializar)")
    estado.validar(json.loads(caminho.read_text("utf-8")))
