"""Alertas por issue do GitHub (Task 35): decide, a partir do estado_fontes.json, quais issues abrir e fechar.

Lógica pura. Quem fala com o GitHub é scripts/sincronizar_issues.py. Regras:
  - abre uma issue quando a fonte falha 2 vezes seguidas (erro/suspeito) ou fica defasada;
  - uma issue por fonte (o título começa com "[ID]"): não duplica enquanto a anterior está aberta;
  - fecha quando a fonte volta a "ok".
"""

import re
from dataclasses import dataclass
from typing import Any

ROTULO = "fonte-com-problema"
FALHAS_PARA_ABRIR = 2
_TITULO = re.compile(r"^\[(TO-[A-Z]{3}-\d{2})\]")


@dataclass(frozen=True)
class Acao:
    tipo: str  # "abrir" | "fechar"
    fonte: str
    titulo: str | None = None
    corpo: str | None = None
    numero: int | None = None


def titulo(id_fonte: str) -> str:
    return f"[{id_fonte}] fonte com problema na atualização diária"


def fonte_da_issue(titulo_issue: str) -> str | None:
    m = _TITULO.match(titulo_issue)
    return m.group(1) if m else None


def _corpo(id_fonte: str, f: dict[str, Any]) -> str:
    return (
        f"A fonte **{id_fonte}** está com status **{f['status']}** "
        f"({f['falhas_consecutivas']} falha(s) seguida(s)).\n\n"
        f"- Última coleta aceita: {f['coletado_em'] or 'nunca'}\n"
        f"- Última confirmação: {f['confirmado_em'] or 'nunca'}\n"
        f"- Último erro: {f['mensagem_erro'] or '(sem mensagem)'}\n\n"
        "O painel continua mostrando o último dado válido. Esta issue fecha sozinha quando a fonte "
        "voltar a `ok`. Para tentar de novo: workflow **Verificar fontes** com `forcar` = o id da fonte."
    )


def precisa_de_issue(f: dict[str, Any]) -> bool:
    if f["status"] == "defasado":
        return True
    return f["status"] in ("erro", "suspeito") and f["falhas_consecutivas"] >= FALHAS_PARA_ABRIR


def planejar(estado: dict[str, Any], abertas: list[dict[str, Any]]) -> list[Acao]:
    """`abertas` = issues abertas com o rótulo, cada uma {"number": int, "title": str}."""
    por_fonte: dict[str, int] = {}
    for issue in abertas:
        fonte = fonte_da_issue(issue["title"])
        if fonte is not None:
            por_fonte.setdefault(fonte, issue["number"])
    acoes = []
    for id_fonte, f in estado["fontes"].items():
        aberta = por_fonte.get(id_fonte)
        if precisa_de_issue(f) and aberta is None:
            acoes.append(Acao("abrir", id_fonte, titulo(id_fonte), _corpo(id_fonte, f)))
        elif f["status"] == "ok" and aberta is not None:
            acoes.append(Acao("fechar", id_fonte, numero=aberta))
    return acoes
