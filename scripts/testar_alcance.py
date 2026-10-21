"""
Sonda de alcance (Task 35, passo 1): testa se as fontes respondem a partir de ONDE este script roda.

    python scripts/testar_alcance.py --origem local --saida alcance_local.json
    python scripts/testar_alcance.py --origem github-actions --comparar alcance_local.json --saida alcance.json

Informativa: endereço inacessível NÃO vira erro (código de saída 0). A lógica está em
src/orquestracao/alcance.py; o relatório de cada ambiente é comparado para achar `bloqueio_rede_runner`.
"""

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.orquestracao import alcance  # noqa: E402


def _imprimir_tabela(rel: dict) -> None:
    for r in rel["resultados"]:
        marca = "ok " if r["acessivel"] else "XX "
        status = r["status_code"] or "-"
        print(f"{marca}{r['id']:<34} {r['classe']:<18} {status!s:>4} {r['latencia_ms']:>6} ms")
    resumo = rel["resumo"]
    print(f"{resumo['acessiveis']} de {resumo['total']} acessíveis a partir de: {rel['origem']}")


def main(argv: list[str] | None = None, alvos: list[alcance.Alvo] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Testa o alcance das fontes a partir deste ambiente.")
    ap.add_argument(
        "--origem", default="local", help="rótulo do ambiente (local, github-actions...)"
    )
    ap.add_argument(
        "--timeout", type=float, default=15.0, help="segundos por requisição (padrão 15)"
    )
    ap.add_argument("--saida", type=Path, help="grava o relatório JSON neste arquivo")
    ap.add_argument(
        "--comparar", type=Path, help="relatório JSON de referência (ex.: o do computador local)"
    )
    ap.add_argument("--resumo-md", type=Path, help="acrescenta a tabela em markdown neste arquivo")
    ap.add_argument(
        "--imprimir-json", action="store_true", help="imprime o JSON entre marcadores no log"
    )
    args = ap.parse_args(argv)
    if args.timeout <= 0:
        ap.error("--timeout precisa ser maior que zero")

    rel = alcance.executar(alvos, timeout=args.timeout, origem=args.origem)
    comparacao = None
    if args.comparar:
        comparacao = alcance.comparar(json.loads(args.comparar.read_text("utf-8")), rel)
        rel["comparacao"] = comparacao
    _imprimir_tabela(rel)
    if comparacao:
        print("comparação:", json.dumps(comparacao["resumo"], ensure_ascii=False))
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(json.dumps(rel, ensure_ascii=False, indent=2), "utf-8")
    if args.resumo_md:
        with args.resumo_md.open("a", encoding="utf-8") as f:
            f.write(alcance.resumo_markdown(rel, comparacao))
    if args.imprimir_json:
        print("BEGIN_ALCANCE_JSON")
        print(json.dumps(rel, ensure_ascii=False))
        print("END_ALCANCE_JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
