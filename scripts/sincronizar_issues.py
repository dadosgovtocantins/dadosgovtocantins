"""
Abre e fecha as issues de alerta das fontes a partir do estado_fontes.json (Task 35).
Usa o `gh` (no workflow, com o GH_TOKEN do próprio GitHub Actions); não grava nada no repositório.

Uso: python scripts/sincronizar_issues.py [--estado CAMINHO] [--simular]
"""

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.orquestracao import estado as arquivo_estado  # noqa: E402
from src.orquestracao.issues import ROTULO, planejar  # noqa: E402

ESTADO = RAIZ / "src" / "ui" / "data" / "estado_fontes.json"


def gh(*args: str) -> str:
    executavel = shutil.which("gh")
    if executavel is None:
        raise OSError("o comando `gh` não foi encontrado")
    return subprocess.run(  # noqa: S603  (lista de argumentos, sem shell)
        [executavel, *args], check=True, capture_output=True, text=True, timeout=60
    ).stdout


def sincronizar(
    estado: dict, executar: Callable[..., str] = gh, simular: bool = False
) -> list[str]:
    """Aplica o plano e devolve o que foi (ou seria) feito, uma linha por ação."""
    abertas = json.loads(
        executar(
            "issue",
            "list",
            "--state",
            "open",
            "--label",
            ROTULO,
            "--json",
            "number,title",
            "--limit",
            "100",
        )
    )
    feitas = []
    for acao in planejar(estado, abertas):
        if acao.tipo == "abrir":
            feitas.append(f"abrir: {acao.titulo}")
            if not simular:
                executar("label", "create", ROTULO, "--force", "--color", "D93F0B")
                executar(
                    "issue",
                    "create",
                    "--title",
                    acao.titulo,
                    "--body",
                    acao.corpo,
                    "--label",
                    ROTULO,
                )
        else:
            feitas.append(f"fechar: #{acao.numero} ({acao.fonte} voltou a ok)")
            if not simular:
                executar(
                    "issue", "close", str(acao.numero), "--comment", f"{acao.fonte} voltou a `ok`."
                )
    return feitas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Abre/fecha as issues de alerta das fontes.")
    ap.add_argument("--estado", type=Path, default=ESTADO)
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args(argv)
    try:
        estado = arquivo_estado.ler(args.estado)
    except arquivo_estado.EstadoInvalidoError as erro:
        print(f"Estado inválido: {erro}", file=sys.stderr)
        return 2
    try:
        feitas = sincronizar(estado, simular=args.simular)
    except (subprocess.SubprocessError, OSError, ValueError) as erro:
        print(f"Falha ao falar com o GitHub: {type(erro).__name__}: {erro}", file=sys.stderr)
        return 1
    print("\n".join(feitas) if feitas else "Nenhuma issue a abrir ou fechar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
