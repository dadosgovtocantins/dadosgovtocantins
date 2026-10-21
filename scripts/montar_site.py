"""
Monta o site público (Task 36) numa pasta: só a lista fixa de arquivos, depois de conferir segredos, dados e
endereços externos. Sincroniza a pasta (não a recria): serve para a publicação incremental.

Uso (da raiz do projeto):
    python scripts/montar_site.py --saida /caminho/do/clone-do-painel
    python scripts/montar_site.py --saida /tmp/site --exigir-padrao   # no workflow: o padrão do e-mail é obrigatório

Código de saída: 0 montado; 1 recusado (nada copiado); 2 uso incorreto.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.orquestracao.site import SiteInvalidoError, montar, padrao_email_infra  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Monta a pasta do site público.")
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--exigir-padrao", action="store_true")
    args = ap.parse_args(argv)
    try:
        r = montar(args.saida, RAIZ, padrao_email_infra(), args.exigir_padrao)
    except SiteInvalidoError as erro:
        print(f"Site recusado: {erro}", file=sys.stderr)
        return 1
    print(
        f"Site em {args.saida}: {r['escritos']} escritos, {r['iguais']} iguais, {r['removidos']} removidos."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
