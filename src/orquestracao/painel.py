"""Funções puras que montam e combinam o painel_dados.json (Task 29, reaproveitadas na Task 35).

Usadas pelo exportador manual (scripts/exportar_painel.py) e pelo orquestrador diário
(src/orquestracao/orquestrador.py): uma só definição do formato do arquivo.
"""

import importlib
import re
from collections import defaultdict
from typing import Any

from src.cli import REGISTRO_COLETORES
from src.orquestracao.fontes import FONTES, IMPLEMENTADOS, TITULARES, TOTAL_MUNICIPIOS

# Indicadores municipais cujo total do estado é a soma dos 139 municípios (só com cobertura completa).
SOMAR_NO_ESTADO = {"populacao_residente", "area_territorial", "producao_agricola", "rebanho_bovino"}


def instanciar(id_fonte: str):
    modulo, classe = REGISTRO_COLETORES[id_fonte]
    return getattr(importlib.import_module(modulo), classe)(ambiente="dev")


def montar_painel(por_fonte: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Agrupa os registros em estado[ind] e municipios[cod][ind]; cada série é [[rótulo, valor], ...]."""
    pontos: dict = defaultdict(lambda: defaultdict(dict))  # ind -> município|None -> periodo_ref
    unidades = {}
    for registros in por_fonte.values():
        for r in registros:
            rotulo = r["valor_texto"] or r["periodo_ref"][:4]
            pontos[r["id_indicador"]][r["id_municipio"]][r["periodo_ref"]] = (
                rotulo,
                r["valor_num"],
            )
            unidades[r["id_indicador"]] = r["unidade"]
    estado: dict[str, list] = {}
    municipios: dict[str, dict] = defaultdict(dict)
    for ind, por_ente in pontos.items():
        for mun, por_periodo in por_ente.items():
            serie = [[rot, v] for _ref, (rot, v) in sorted(por_periodo.items())]
            if mun is None:
                estado[ind] = serie
            else:
                municipios[mun][ind] = serie
        if ind in SOMAR_NO_ESTADO and ind not in estado:
            totais: dict = defaultdict(list)
            for por_periodo in por_ente.values():
                for ref, ponto in por_periodo.items():
                    totais[ref].append(ponto)
            serie = [
                [v[0][0], round(sum(p[1] for p in v), 3)]
                for _ref, v in sorted(totais.items())
                if len(v) == TOTAL_MUNICIPIOS
            ]
            if serie:
                estado[ind] = serie
    return {"unidades": unidades, "estado": estado, "municipios": dict(municipios)}


def montar_titulares(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """dim_titular -> {"estado": {...}, "municipios": {cod: {...}}}, só com nome, cargo, ano e fonte."""

    def item(r: dict[str, Any]) -> dict[str, Any]:
        return {
            "nome": r["nome_titular"],
            "cargo": r["cargo"],
            "ano_eleicao": r["ano_eleicao"],
            "fonte": r["fonte"],
        }

    return {
        "estado": next((item(r) for r in registros if r["id_municipio"] is None), None),
        "municipios": {r["id_municipio"]: item(r) for r in registros if r["id_municipio"]},
    }


def reaproveitar(painel: dict, fontes: dict, anterior: dict, id_fonte: str) -> None:
    """Fonte pulada: copia do arquivo anterior o que ela produziu (ou marca como sem dado anterior)."""
    ind = instanciar(id_fonte).id_indicador
    meta = anterior.get("fontes", {}).get(id_fonte)
    sem_titulares = id_fonte == TITULARES and not anterior.get("titulares")
    if not meta or meta.get("status") != "ok" or sem_titulares:
        fontes[id_fonte] = {
            "indicador": ind,
            "status": "erro",
            "erro": "pulada e sem dado anterior",
        }
        return
    fontes[id_fonte] = meta
    if id_fonte == TITULARES:
        painel["titulares"] = anterior["titulares"]
        return
    painel["unidades"][ind] = anterior["unidades"][ind]
    if ind in anterior["estado"]:
        painel["estado"][ind] = anterior["estado"][ind]
    for mun, inds in anterior["municipios"].items():
        if ind in inds:
            painel["municipios"].setdefault(mun, {})[ind] = inds[ind]


# --- Task 35: mesclar o SICONFI por município e consolidar o arquivo --------------------------------

_ANO = re.compile(r"^\d{4}$")


def mesclar_serie(antiga: list[list], nova: list[list]) -> list[list]:
    """União por ano de duas séries [[AAAA, valor], ...]; o valor novo vence. Só para séries anuais."""
    por_ano: dict[str, Any] = {}
    for rotulo, valor in [*antiga, *nova]:
        if not _ANO.match(str(rotulo)):
            raise ValueError(f"mesclar_serie só aceita rótulo anual (AAAA), veio {rotulo!r}")
        por_ano[str(rotulo)] = valor
    return [[ano, por_ano[ano]] for ano in sorted(por_ano)]


def mesclar_indicador(painel: dict, anterior: dict, ind: str) -> None:
    """Preserva no `painel` novo o que o `anterior` já tinha do indicador (piso do SICONFI).

    Município que atrasou a entrega mantém o valor anterior; entrega nova e retificação entram; município
    sem valor continua ausente (nunca zero). A cobertura por exercício nunca diminui.
    """
    painel["unidades"].setdefault(ind, anterior.get("unidades", {}).get(ind))
    if anterior.get("estado", {}).get(ind):
        painel["estado"][ind] = mesclar_serie(
            anterior["estado"][ind], painel["estado"].get(ind, [])
        )
    for mun, series in anterior.get("municipios", {}).items():
        if ind in series:
            destino = painel["municipios"].setdefault(mun, {})
            destino[ind] = mesclar_serie(series[ind], destino.get(ind, []))


def consolidar(
    anterior: dict | None, aceitas: dict[str, list[dict[str, Any]]], agora_iso: str
) -> dict:
    """painel_dados.json novo: as fontes `aceitas` trocam as suas séries; as demais mantêm o `anterior`.

    A receita do SICONFI é mesclada por município (ver mesclar_indicador). Fonte sem dado anterior e sem
    coleta aceita fica com status "erro" (o painel mostra "Não coletado").
    """
    anterior = anterior or {"fontes": {}, "unidades": {}, "estado": {}, "municipios": {}}
    series = {f: r for f, r in aceitas.items() if f != TITULARES}
    painel = montar_painel(series)
    fontes: dict[str, Any] = {
        f: {
            "indicador": instanciar(f).id_indicador,
            "coletado_em": agora_iso,
            "status": "ok",
            "registros": len(registros),
        }
        for f, registros in series.items()
    }
    for f in IMPLEMENTADOS:
        if f not in series:
            reaproveitar(painel, fontes, anterior, f)
    if "TO-REC-02" in series:
        mesclar_indicador(painel, anterior, "receita_corrente_liquida")
    if TITULARES in aceitas:
        painel["titulares"] = montar_titulares(aceitas[TITULARES])
        fontes[TITULARES] = {
            "indicador": instanciar(TITULARES).id_indicador,
            "coletado_em": agora_iso,
            "status": "ok",
            "registros": len(aceitas[TITULARES]),
        }
    else:
        reaproveitar(painel, fontes, anterior, TITULARES)
    return {"gerado_em": agora_iso, "fontes": {f: fontes[f] for f in FONTES}, **painel}
