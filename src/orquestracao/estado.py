"""estado_fontes.json: o que o orquestrador sabe de cada fonte (Task 35, passo 3).

Versionado em src/ui/data/estado_fontes.json. O painel mostra "verificado em" e o status por fonte a partir dele.
Validação rígida (chave desconhecida é recusada) e escrita atômica: nunca fica um arquivo pela metade.
"""

import json
import os
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from src.orquestracao.fontes import FONTES

VERSAO = 1
STATUS = ("ok", "erro", "defasado", "suspeito")
MAX_MENSAGEM = 300
CAMPOS_TOPO = {"versao", "ultima_execucao_orquestrador", "fontes"}
CAMPOS_DATA_HORA = ("verificado_em", "coletado_em", "confirmado_em")
CAMPOS_TEXTO = ("ultimo_periodo_coletado", "marca_sentinela", "mensagem_erro")
CAMPOS_FONTE = {
    *CAMPOS_DATA_HORA,
    *CAMPOS_TEXTO,
    "status",
    "falhas_consecutivas",
    "proxima_divulgacao",
}
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DIA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class EstadoInvalidoError(ValueError):
    """estado_fontes.json fora do schema ou ilegível."""


def para_iso(momento: datetime) -> str:
    """UTC, sem fração de segundo: '2026-10-21T17:00:12Z'. Data sem fuso é recusada (ambígua)."""
    if momento.tzinfo is None:
        raise ValueError("data e hora sem fuso: informe o fuso (UTC) para evitar ambiguidade")
    return momento.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def de_iso(texto: str | None) -> datetime | None:
    return (
        None
        if texto is None
        else datetime.strptime(texto, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    )


def fonte_vazia() -> dict[str, Any]:
    return {
        "ultimo_periodo_coletado": None,
        "marca_sentinela": None,
        "verificado_em": None,
        "coletado_em": None,
        "confirmado_em": None,
        "status": "erro",
        "falhas_consecutivas": 0,
        "mensagem_erro": "ainda não coletada",
        "proxima_divulgacao": None,
    }


def estado_vazio(agora: datetime | None = None) -> dict[str, Any]:
    agora = agora or datetime.now(UTC)
    return {
        "versao": VERSAO,
        "ultima_execucao_orquestrador": para_iso(agora),
        "fontes": {f: fonte_vazia() for f in FONTES},
    }


def _recusar(onde: str, motivo: str) -> None:
    raise EstadoInvalidoError(f"{onde}: {motivo}")


def _data_hora(onde: str, valor: Any, obrigatorio: bool = False) -> None:
    if valor is None and not obrigatorio:
        return
    if not isinstance(valor, str) or not _UTC.match(valor):
        _recusar(onde, f"esperado AAAA-MM-DDTHH:MM:SSZ (UTC), veio {valor!r}")
    try:
        de_iso(valor)
    except ValueError:
        _recusar(onde, f"data inexistente: {valor!r}")


def _validar_fonte(id_fonte: str, f: Any) -> None:
    onde = f"fontes.{id_fonte}"
    if not isinstance(f, dict):
        _recusar(onde, "esperado um objeto")
    faltam, sobram = CAMPOS_FONTE - set(f), set(f) - CAMPOS_FONTE
    if faltam or sobram:
        _recusar(onde, f"campos faltando {sorted(faltam)}, desconhecidos {sorted(sobram)}")
    for campo in CAMPOS_DATA_HORA:
        _data_hora(f"{onde}.{campo}", f[campo])
    for campo in CAMPOS_TEXTO:
        v = f[campo]
        if v is not None and (not isinstance(v, str) or not v):
            _recusar(f"{onde}.{campo}", f"esperado texto não vazio ou null, veio {v!r}")
    msg = f["mensagem_erro"]
    if msg is not None and (len(msg) > MAX_MENSAGEM or "\n" in msg or "\r" in msg):
        _recusar(f"{onde}.mensagem_erro", f"até {MAX_MENSAGEM} caracteres e numa linha só")
    if f["status"] not in STATUS:
        _recusar(f"{onde}.status", f"esperado um de {STATUS}, veio {f['status']!r}")
    n = f["falhas_consecutivas"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        _recusar(f"{onde}.falhas_consecutivas", f"esperado inteiro >= 0, veio {n!r}")
    prox = f["proxima_divulgacao"]
    if prox is not None:
        if not isinstance(prox, str) or not _DIA.match(prox):
            _recusar(f"{onde}.proxima_divulgacao", f"esperado AAAA-MM-DD, veio {prox!r}")
        try:
            date.fromisoformat(prox)
        except ValueError:
            _recusar(f"{onde}.proxima_divulgacao", f"data inexistente: {prox!r}")


def validar(e: Any) -> None:
    """Levanta EstadoInvalidoError se `e` não for um estado_fontes.json válido."""
    if not isinstance(e, dict):
        _recusar("estado", "esperado um objeto JSON")
    faltam, sobram = CAMPOS_TOPO - set(e), set(e) - CAMPOS_TOPO
    if faltam or sobram:
        _recusar("estado", f"campos faltando {sorted(faltam)}, desconhecidos {sorted(sobram)}")
    if e["versao"] != VERSAO or isinstance(e["versao"], bool):
        _recusar("versao", f"esperado {VERSAO}, veio {e['versao']!r}")
    _data_hora("ultima_execucao_orquestrador", e["ultima_execucao_orquestrador"], obrigatorio=True)
    fontes = e["fontes"]
    if not isinstance(fontes, dict):
        _recusar("fontes", "esperado um objeto")
    if set(fontes) != set(FONTES):
        _recusar(
            "fontes",
            f"esperadas exatamente as 9 fontes; faltam {sorted(set(FONTES) - set(fontes))}, sobram {sorted(set(fontes) - set(FONTES))}",
        )
    for id_fonte in FONTES:
        _validar_fonte(id_fonte, fontes[id_fonte])


def ler(caminho: Path) -> dict[str, Any]:
    caminho = Path(caminho)
    if not caminho.exists():
        raise EstadoInvalidoError(f"{caminho} não existe (rode scripts/atualizar.py --inicializar)")
    try:
        e = json.loads(caminho.read_text("utf-8"))
    except ValueError as erro:
        raise EstadoInvalidoError(f"{caminho} não é JSON válido: {erro}") from erro
    validar(e)
    return e


def gravar(caminho: Path, e: dict[str, Any]) -> None:
    """Valida e grava de forma atômica (arquivo temporário + troca); em qualquer falha o original fica intacto."""
    validar(e)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # ordem estável (a das fontes do catálogo) para o diff do Git ser legível
    ordenado = {**e, "fontes": {f: e["fontes"][f] for f in FONTES}}
    texto = json.dumps(ordenado, ensure_ascii=False, indent=2) + "\n"
    temporario = caminho.with_name(f"{caminho.name}.{os.getpid()}.tmp")
    try:
        temporario.write_text(texto, "utf-8")
        temporario.replace(caminho)
    finally:
        temporario.unlink(missing_ok=True)
