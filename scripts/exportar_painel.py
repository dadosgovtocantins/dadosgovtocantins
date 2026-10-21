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
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.orquestracao.fontes import (  # noqa: E402,F401  (reexportados: carregar_bigquery.py os usa daqui)
    FONTES,
    IMPLEMENTADOS,
    TITULARES,
    TOTAL_MUNICIPIOS,
)
from src.orquestracao.painel import (  # noqa: E402,F401
    SOMAR_NO_ESTADO,
    instanciar,
    montar_painel,
    montar_titulares,
    reaproveitar,
)

SAIDA = RAIZ / "src" / "ui" / "data" / "painel_dados.json"


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
