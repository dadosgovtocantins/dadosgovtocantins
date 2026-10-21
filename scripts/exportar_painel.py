"""
Exporta os dados REAIS dos coletores para o painel (Task 29): src/ui/data/painel_dados.json.

Roda os coletores reais (IBGE e Tesouro) sem passar pela carga: extrai, transforma e agrupa por
município e por estado. Falha de uma fonte não derruba as demais: ela vai para fontes[id].erro e o
painel mostra "Não coletado" nos indicadores dessa fonte. Sem nenhuma fonte ok, o arquivo não é tocado.
Os titulares eleitos (TO-GER-01, TSE; Task 32) não são série: vão para "titulares", só se validados.

Uso (da raiz do projeto):
    python scripts/exportar_painel.py                      # todas (TO-REC-02 leva ~20 min)
    python scripts/exportar_painel.py --pular TO-REC-02    # reaproveita o que já está no arquivo
"""

import argparse
import importlib
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.cli import REGISTRO_COLETORES  # noqa: E402

SAIDA = RAIZ / "src" / "ui" / "data" / "painel_dados.json"
IMPLEMENTADOS = [
    "TO-TER-01",
    "TO-TER-02",
    "TO-TER-03",
    "TO-TER-04",
    "TO-TER-05",
    "TO-TER-06",
    "TO-TER-07",
    "TO-REC-02",
]
TITULARES = "TO-GER-01"  # dim_titular: nome do prefeito/governador eleito, fora das séries
FONTES = [*IMPLEMENTADOS, TITULARES]
# Indicadores municipais cujo total do estado é a soma dos 139 municípios (só com cobertura completa).
SOMAR_NO_ESTADO = {"populacao_residente", "area_territorial", "producao_agricola", "rebanho_bovino"}
TOTAL_MUNICIPIOS = 139


def instanciar(id_fonte: str):
    modulo, classe = REGISTRO_COLETORES[id_fonte]
    return getattr(importlib.import_module(modulo), classe)(ambiente="dev")


def coletar(id_fonte: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    coletor = instanciar(id_fonte)
    meta = {"indicador": coletor.id_indicador, "coletado_em": datetime.now(UTC).isoformat()}
    try:
        registros = coletor.transformar(coletor.extrair())
        if not registros:
            raise ValueError("a fonte não devolveu nenhum registro")
        if id_fonte == TITULARES:
            coletor.validar(
                registros
            )  # validar_titulares: 139 municípios, 1 governador, sem duplicata
    except Exception as e:
        return [], {**meta, "status": "erro", "erro": f"{type(e).__name__}: {e}"[:300]}
    return registros, {**meta, "status": "ok", "registros": len(registros)}


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Exporta os dados reais dos coletores para o painel.")
    ap.add_argument("--pular", nargs="*", default=[], choices=FONTES)
    ap.add_argument("--saida", type=Path, default=SAIDA)
    args = ap.parse_args(argv)

    anterior = json.loads(args.saida.read_text("utf-8")) if args.saida.exists() else {}
    registros, fontes = {}, {}
    for id_fonte in FONTES:
        if id_fonte in args.pular:
            continue
        print(f"[{datetime.now():%H:%M:%S}] coletando {id_fonte}...", flush=True)
        registros[id_fonte], fontes[id_fonte] = coletar(id_fonte)
        print(
            f"    {fontes[id_fonte]['status']}: {fontes[id_fonte].get('registros', fontes[id_fonte].get('erro'))}"
        )
    if not any(m["status"] == "ok" for m in fontes.values()):
        print("Nenhuma fonte coletada: o arquivo do painel não foi alterado.", file=sys.stderr)
        return 1

    titulares = registros.pop(TITULARES, [])
    painel = montar_painel(registros)
    if titulares:
        painel["titulares"] = montar_titulares(titulares)
    for id_fonte in args.pular:
        reaproveitar(painel, fontes, anterior, id_fonte)
    saida = {"gerado_em": datetime.now(UTC).isoformat(), "fontes": fontes, **painel}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = args.saida.with_suffix(".tmp")
    temporario.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), "utf-8")
    temporario.replace(args.saida)
    ok = sum(m["status"] == "ok" for m in fontes.values())
    print(
        f"Exportado: {args.saida} ({ok}/{len(FONTES)} fontes ok, {len(painel['municipios'])} municípios)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
