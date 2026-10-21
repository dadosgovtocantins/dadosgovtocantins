"""
Atualização diária do painel (Task 35): verifica as 9 fontes, coleta só o que tem novidade, valida e grava
src/ui/data/painel_dados.json (só se houver dado novo aceito) e src/ui/data/estado_fontes.json (sempre).

Uso (da raiz do projeto):
    python scripts/atualizar.py                          # rotina diária
    python scripts/atualizar.py --forcar TO-TER-04       # coleta a fonte mesmo sem novidade
    python scripts/atualizar.py --forcar todas           # coleta as 9 (o SICONFI leva ~20 min)
    python scripts/atualizar.py --inicializar            # cria o estado a partir do painel atual, sem coletar

Código de saída: 0 quando a execução terminou (mesmo com fontes em erro: o estado as registra e o
workflow abre as issues); 2 para uso incorreto ou arquivo de estado inválido.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.coletor_base.http import ClienteHTTP  # noqa: E402
from src.coletores.tse_candidatos import hoje as hoje_brasilia  # noqa: E402
from src.orquestracao import estado as arquivo_estado  # noqa: E402
from src.orquestracao.fontes import FONTES  # noqa: E402
from src.orquestracao.historico import historico_estadual  # noqa: E402
from src.orquestracao.orquestrador import executar  # noqa: E402
from src.orquestracao.painel import instanciar  # noqa: E402
from src.orquestracao.sentinelas import SentinelaError, Sentinelas  # noqa: E402

DADOS = RAIZ / "src" / "ui" / "data"
PAINEL = DADOS / "painel_dados.json"
ESTADO = DADOS / "estado_fontes.json"


def coletar(id_fonte: str) -> list[dict]:
    coletor = instanciar(id_fonte)
    return coletor.transformar(coletor.extrair())


def gravar_painel(caminho: Path, painel: dict) -> None:
    temporario = caminho.with_suffix(".tmp")
    try:
        temporario.write_text(
            json.dumps(painel, ensure_ascii=False, separators=(",", ":")), "utf-8"
        )
        temporario.replace(caminho)
    finally:
        temporario.unlink(missing_ok=True)


def ids_forcados(valor: str | None) -> list[str]:
    """`--forcar` aceita só ids conhecidos (separados por vírgula) ou `todas`; qualquer outra coisa é recusada."""
    if not valor:
        return []
    if valor.strip() == "todas":
        return list(FONTES)
    ids = [i.strip() for i in valor.split(",") if i.strip()]
    desconhecidos = [i for i in ids if i not in FONTES]
    if desconhecidos or not ids:
        raise ValueError(
            f"--forcar: fonte desconhecida {desconhecidos or [valor]}; use {FONTES} ou 'todas'"
        )
    return ids


def inicializar(painel: dict | None, sentinelas: Sentinelas, agora: datetime) -> dict:
    """Estado inicial a partir do painel já publicado e das sentinelas de hoje, SEM coletar."""
    estado = arquivo_estado.estado_vazio(agora)
    t = arquivo_estado.para_iso(agora)
    for id_fonte in FONTES:
        meta = ((painel or {}).get("fontes") or {}).get(id_fonte) or {}
        if meta.get("status") != "ok":
            continue  # sem dado válido no painel: continua "ainda não coletada" e será coletada
        try:
            s = sentinelas.consultar(id_fonte)
        except SentinelaError as erro:
            print(
                f"  {id_fonte}: sentinela fora ({erro}); fica para a primeira execução",
                file=sys.stderr,
            )
            continue
        coletado = arquivo_estado.para_iso(datetime.fromisoformat(meta["coletado_em"]))
        estado["fontes"][id_fonte].update(
            ultimo_periodo_coletado=s.ultimo_periodo,
            marca_sentinela=s.marca,
            verificado_em=t,
            coletado_em=coletado,
            confirmado_em=t,
            status="ok",
            mensagem_erro=None,
            proxima_divulgacao=s.proxima_divulgacao,
        )
    return estado


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Atualização diária do painel.")
    ap.add_argument("--forcar", default=None, help="ids separados por vírgula, ou 'todas'")
    ap.add_argument("--inicializar", action="store_true")
    ap.add_argument("--estado", type=Path, default=ESTADO)
    ap.add_argument("--painel", type=Path, default=PAINEL)
    args = ap.parse_args(argv)
    try:
        forcar = ids_forcados(args.forcar)
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 2

    agora = datetime.now(UTC)
    http = ClienteHTTP(delay_segundos=0.2)
    sentinelas = Sentinelas(http.get, hoje_brasilia())
    painel = json.loads(args.painel.read_text("utf-8")) if args.painel.exists() else None

    if args.inicializar:
        estado = inicializar(painel, sentinelas, agora)
        arquivo_estado.gravar(args.estado, estado)
        iniciais = sum(f["coletado_em"] is not None for f in estado["fontes"].values())
        print(
            f"Estado inicial gravado em {args.estado} ({iniciais}/{len(FONTES)} fontes com dado)."
        )
        return 0

    try:
        estado = arquivo_estado.ler(args.estado)
    except arquivo_estado.EstadoInvalidoError as erro:
        print(f"Estado inválido: {erro}", file=sys.stderr)
        return 2

    resultado = executar(
        estado=estado,
        painel_anterior=painel,
        agora=agora,
        forcar=forcar,
        sentinelas=sentinelas,
        coletar=coletar,
        historico=historico_estadual,
    )
    for id_fonte in FONTES:
        print(f"{id_fonte}: {resultado.relatorio[id_fonte]}")
    if resultado.painel is not None:
        gravar_painel(args.painel, resultado.painel)
    arquivo_estado.gravar(args.estado, resultado.estado)
    print(f"Painel {'atualizado' if resultado.painel else 'sem alteração'}; estado gravado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
