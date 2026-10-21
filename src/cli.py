"""Entrypoint dos Cloud Run Jobs.

Despacha coletores registrados por ID de fonte.
PRD v4.2, Task 06 (framework) e Task 08 (Bloco IBGE).
"""

import argparse
import json
import sys

from src import AVISO_NAO_OFICIALIDADE, __version__

# Registro de coletores: id_fonte → (módulo, classe)
REGISTRO_COLETORES: dict[str, tuple[str, str]] = {
    "TO-TER-01": ("src.coletores.to_ter_01", "ColetorTOTER01"),
    "TO-TER-02": ("src.coletores.to_ter_02", "ColetorTOTER02"),
    "TO-TER-03": ("src.coletores.to_ter_03", "ColetorTOTER03"),
    "TO-TER-04": ("src.coletores.to_ter_04", "ColetorTOTER04"),
    "TO-TER-05": ("src.coletores.to_ter_05", "ColetorTOTER05"),
    "TO-TER-06": ("src.coletores.to_ter_06", "ColetorTOTER06"),
    "TO-TER-07": ("src.coletores.to_ter_07", "ColetorTOTER07"),
    "TO-EDU-01": ("src.coletores.to_edu_01", "ColetorTOEDU01"),
    "TO-EDU-02": ("src.coletores.to_edu_02", "ColetorTOEDU02"),
    "TO-TRAB-01": ("src.coletores.to_trab_01", "ColetorTOTRAB01"),
    "TO-ECO-01": ("src.coletores.to_eco_01", "ColetorTOECO01"),
    "TO-ECO-02": ("src.coletores.to_eco_02", "ColetorTOECO02"),
    "TO-SAU-01": ("src.coletores.to_sau_01", "ColetorTOSAU01"),
    "TO-SAU-02": ("src.coletores.to_sau_02", "ColetorTOSAU02"),
    "TO-SAU-03": ("src.coletores.to_sau_03", "ColetorTOSAU03"),
    "TO-REC-01": ("src.coletores.to_rec_01", "ColetorTOREC01"),
    "TO-REC-02": ("src.coletores.to_rec_02", "ColetorTOREC02"),
    "TO-REC-03": ("src.coletores.to_rec_03", "ColetorTOREC03"),
    "TO-GER-01": ("src.coletores.to_ger_01", "ColetorTOGER01"),
    "TO-GER-02": ("src.coletores.to_ger_02", "ColetorTOGER02"),
}


def _instanciar_coletor(id_fonte: str, ambiente: str):
    """Importa e instancia dinamicamente o coletor pelo id_fonte."""
    import importlib

    if id_fonte not in REGISTRO_COLETORES:
        return None
    modulo_path, classe_nome = REGISTRO_COLETORES[id_fonte]
    modulo = importlib.import_module(modulo_path)
    cls = getattr(modulo, classe_nome)
    return cls(ambiente=ambiente)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="painel-to",
        description=f"Painel TO em Dados v{__version__}. {AVISO_NAO_OFICIALIDADE}",
    )
    sub = parser.add_subparsers(dest="comando")

    coletar = sub.add_parser("coletar", help="Executa o coletor de uma fonte do catálogo")
    coletar.add_argument("--fonte", required=True, help="ID da fonte no catalogo_fontes")
    coletar.add_argument("--ambiente", required=True, choices=["dev", "hml", "prod"])

    sub.add_parser("listar-fontes", help="Lista fontes cadastradas")

    args = parser.parse_args(argv)

    if args.comando == "listar-fontes":
        for fid in sorted(REGISTRO_COLETORES.keys()):
            print(fid)
        return 0

    if args.comando == "coletar":
        coletor = _instanciar_coletor(args.fonte, args.ambiente)
        if coletor is None:
            print(
                json.dumps(
                    {
                        "status": "fonte_nao_cadastrada",
                        "id_fonte": args.fonte,
                        "ambiente": args.ambiente,
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        resultado = coletor.executar()
        print(json.dumps(resultado, ensure_ascii=False, default=str))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
