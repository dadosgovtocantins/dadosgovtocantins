"""
Backtest da trava de 3σ (Task 35): aplica a regra a cada ponto histórico das séries estaduais reais e mostra
quais teriam sido marcados como suspeitos (sem piso e com o piso da política). Meta: no máximo 5% marcados.

Uso (da raiz do projeto; faz 3 consultas à API do IBGE):
    python scripts/backtest_3sigma.py
    python scripts/backtest_3sigma.py --piso TO-TER-07=5     # testa outro piso para a fonte
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.orquestracao.historico import historico_estadual  # noqa: E402
from src.orquestracao.validacao import POLITICA_3SIGMA, backtest  # noqa: E402

LIMITE_PERCENTUAL = 5.0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Backtest do 3σ nas séries estaduais reais.")
    ap.add_argument("--piso", action="append", default=[], metavar="FONTE=VALOR")
    args = ap.parse_args(argv)
    pisos = {f: p for f, (_, _, p) in POLITICA_3SIGMA.items()}
    for item in args.piso:
        fonte, _, valor = item.partition("=")
        if fonte not in pisos or not valor.replace(".", "", 1).isdigit():
            print(
                f"--piso inválido: {item!r} (use FONTE=VALOR, FONTE em {sorted(pisos)})",
                file=sys.stderr,
            )
            return 2
        pisos[fonte] = float(valor)

    estourou = False
    for fonte, (indicador, modo, _) in POLITICA_3SIGMA.items():
        serie = historico_estadual(fonte)
        sem, com = backtest(serie, modo, 0.0), backtest(serie, modo, pisos[fonte])
        unidade = "%" if modo == "pct" else "p.p."
        print(
            f"\n{fonte} {indicador}: {len(serie)} pontos ({serie[0][0]} a {serie[-1][0]}), variação em {unidade}"
        )
        print(
            f"  sem piso : {len(sem['marcados'])} de {sem['avaliados']} marcados ({sem['percentual']:.1f}%)"
        )
        for m in sem["marcados"]:
            print(f"             {m['rotulo']}: {m['variacao']:+.2f}")
        print(
            f"  piso {pisos[fonte]:g}: {len(com['marcados'])} de {com['avaliados']} marcados ({com['percentual']:.1f}%)"
        )
        for m in com["marcados"]:
            print(f"             {m['rotulo']}: {m['variacao']:+.2f}")
        estourou |= com["percentual"] > LIMITE_PERCENTUAL
    print(
        f"\nLimite de {LIMITE_PERCENTUAL:g}% marcados: {'ESTOUROU' if estourou else 'respeitado'}."
    )
    return 1 if estourou else 0


if __name__ == "__main__":
    sys.exit(main())
