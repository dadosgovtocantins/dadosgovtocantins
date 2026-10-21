"""Orquestrador diário (Task 35, passo 7): para cada fonte, pergunta à sentinela se há novidade, coleta só
quando há, valida e decide o que publicar.

Função pura: as dependências (sentinelas, coleta, histórico) entram por parâmetro e nada é lido nem gravado
aqui. Quem lê/grava os arquivos é scripts/atualizar.py.

Regras:
  - sem novidade → não coleta; só confirma a fonte (`verificado_em`, `confirmado_em`);
  - novidade, `forcar` ou recoleta fixa → coleta a fonte inteira e valida (cobertura, integridade e 3σ);
  - aceita → painel e estado atualizados; recusada ou com falha → o dado anterior continua no painel, o
    estado registra erro/suspeito e `falhas_consecutivas + 1`; nada é zerado;
  - a `marca` da sentinela só é guardada quando a coleta é aceita (senão a fonte é tentada de novo amanhã);
  - `defasado` quando a fonte não é CONFIRMADA atual há mais que o prazo da periodicidade + 50%.
"""

import copy
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from typing import Any, Protocol

from src.orquestracao.estado import de_iso, para_iso
from src.orquestracao.fontes import FONTES, PERIODICIDADE, PRAZO_DEFASADO_DIAS, RECOLETA_FIXA_DIAS
from src.orquestracao.painel import consolidar
from src.orquestracao.sentinelas import Sentinela, SentinelaError
from src.orquestracao.validacao import ColetaRecusada, validar_fonte

MAX_MENSAGEM = 300


class ConsultaSentinela(Protocol):
    def consultar(self, id_fonte: str) -> Sentinela: ...


class Resultado:
    """O que a execução produziu: o estado novo, o painel novo (None se nada foi aceito) e o relatório."""

    def __init__(
        self, estado: dict, painel: dict | None, aceitas: list[str], relatorio: dict[str, str]
    ):
        self.estado, self.painel, self.aceitas, self.relatorio = estado, painel, aceitas, relatorio


def _mensagem(erro: BaseException) -> str:
    texto = " ".join(f"{type(erro).__name__}: {erro}".split())
    return texto[:MAX_MENSAGEM]


def _precisa_recoletar(f: dict, id_fonte: str, agora: datetime) -> bool:
    dias = RECOLETA_FIXA_DIAS.get(id_fonte)
    coletado = de_iso(f["coletado_em"])
    return dias is not None and coletado is not None and agora - coletado >= timedelta(days=dias)


def _defasar(f: dict, id_fonte: str, agora: datetime) -> None:
    confirmado = de_iso(f["confirmado_em"])
    prazo = timedelta(days=PRAZO_DEFASADO_DIAS[PERIODICIDADE[id_fonte]])
    if confirmado is not None and agora - confirmado > prazo:
        f["status"] = "defasado"


def _falhou(f: dict, status: str, erro: BaseException | str) -> None:
    f["status"] = status
    f["falhas_consecutivas"] += 1
    f["mensagem_erro"] = erro if isinstance(erro, str) else _mensagem(erro)


def executar(
    *,
    estado: dict[str, Any],
    painel_anterior: dict[str, Any] | None,
    agora: datetime,
    forcar: Iterable[str],
    sentinelas: ConsultaSentinela,
    coletar: Callable[[str], list[dict[str, Any]]],
    historico: Callable[[str], list[list]],
) -> Resultado:
    forcadas = set(forcar)
    t = para_iso(agora)
    novo = copy.deepcopy(estado)
    novo["ultima_execucao_orquestrador"] = t
    aceitas: dict[str, list[dict[str, Any]]] = {}
    relatorio: dict[str, str] = {}

    for id_fonte in FONTES:
        f = novo["fontes"][id_fonte]
        sentinela: Sentinela | None = None
        try:
            sentinela = sentinelas.consultar(id_fonte)
            f["verificado_em"] = t
            f["proxima_divulgacao"] = sentinela.proxima_divulgacao
        except SentinelaError as erro:
            if id_fonte not in forcadas:
                _falhou(f, "erro", erro)
                relatorio[id_fonte] = f"sentinela falhou: {f['mensagem_erro']}"
                _defasar(f, id_fonte, agora)
                continue

        novidade = (sentinela is not None and sentinela.marca != f["marca_sentinela"]) or f[
            "coletado_em"
        ] is None
        if not (id_fonte in forcadas or novidade or _precisa_recoletar(f, id_fonte, agora)):
            f.update(confirmado_em=t, status="ok", falhas_consecutivas=0, mensagem_erro=None)
            relatorio[id_fonte] = "sem novidade"
            _defasar(f, id_fonte, agora)
            continue

        try:
            registros = coletar(id_fonte)
            validar_fonte(id_fonte, registros, historico)
        except ColetaRecusada as erro:
            _falhou(f, "suspeito" if erro.suspeito else "erro", str(erro))
            relatorio[id_fonte] = f"{f['status']}: {f['mensagem_erro']}"
        except Exception as erro:  # rede, formato, histórico indisponível: nada é publicado
            _falhou(f, "erro", erro)
            relatorio[id_fonte] = f"erro: {f['mensagem_erro']}"
        else:
            aceitas[id_fonte] = registros
            if sentinela is not None:
                f["marca_sentinela"] = sentinela.marca
                f["ultimo_periodo_coletado"] = sentinela.ultimo_periodo
            f.update(
                coletado_em=t,
                confirmado_em=t,
                status="ok",
                falhas_consecutivas=0,
                mensagem_erro=None,
            )
            relatorio[id_fonte] = f"coletada ({len(registros)} registros)"
        _defasar(f, id_fonte, agora)

    painel = consolidar(painel_anterior, aceitas, t) if aceitas else None
    return Resultado(novo, painel, list(aceitas), relatorio)
