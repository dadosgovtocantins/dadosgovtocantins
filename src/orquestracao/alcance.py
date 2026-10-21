"""Sonda de alcance (Task 35, passo 1): as fontes respondem a partir deste computador / do runner do GitHub?

Faz UMA requisição leve por endereço (HEAD, ou GET que fecha a conexão sem baixar o corpo; FTP lista um
diretório), com a mesma verificação de TLS dos coletores (certifi + intermediário do IBGE) e sem nova
tentativa. Nenhum endereço derruba os demais: todo erro vira uma `classe` no relatório. Comparar o relatório
do runner com o do computador local é o que revela bloqueio de rede (`bloqueio_rede_runner`).
"""

import ftplib
import platform
import socket
import ssl
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from urllib.parse import unquote, urlsplit

import urllib3
from urllib3.util import Retry

from src.coletor_base.http import USER_AGENT_OFICIAL, _contexto_tls

TAM_MAX_ERRO = 160


@dataclass(frozen=True)
class Alvo:
    id: str
    fonte: str
    uso: str  # "atual" (fonte já coletada) | "futuro" (tasks 39 a 45)
    url: str
    metodo: str = "GET"  # GET | HEAD | FTP
    esperado_401: bool = False  # API que exige chave: 401 prova que o servidor respondeu


def _ibge(agregado: str) -> Alvo:
    return Alvo(
        f"ibge-periodos-{agregado}",
        "IBGE",
        "atual",
        f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos",
    )


_SICONFI = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
_TSE = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip"
_INEP = "https://download.inep.gov.br"
_DATASUS = "ftp://ftp.datasus.gov.br/dissemin/publicos"

ALVOS: list[Alvo] = [
    # --- fontes que o painel já coleta -------------------------------------------------------------
    *[_ibge(a) for a in ("6579", "5938", "4714", "5457", "3939", "4099")],
    Alvo(
        "ibge-dados-populacao",
        "IBGE",
        "atual",
        "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N3[17]",
    ),
    Alvo(
        "ibge-municipios-to",
        "IBGE",
        "atual",
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados/17/municipios",
    ),
    Alvo(
        "ibge-calendario",
        "IBGE",
        "atual",
        "https://servicodados.ibge.gov.br/api/v3/calendario/?qtd=1",
    ),
    Alvo(
        "siconfi-rreo-anexo3",
        "SICONFI",
        "atual",
        f"{_SICONFI}/rreo?an_exercicio=2025&nr_periodo=6&co_tipo_demonstrativo=RREO"
        "&no_anexo=RREO-Anexo%2003&id_ente=17",
    ),
    Alvo(
        "siconfi-rgf-anexo1",
        "SICONFI",
        "atual",
        f"{_SICONFI}/rgf?an_exercicio=2025&in_periodicidade=Q&nr_periodo=3&co_tipo_demonstrativo=RGF"
        "&co_poder=E&no_anexo=RGF-Anexo%2001&id_ente=17",
    ),
    Alvo(
        "siconfi-extrato-entregas",
        "SICONFI",
        "atual",
        f"{_SICONFI}/extrato_entregas?id_ente=17&an_referencia=2025",
    ),
    Alvo("tse-candidatos-2024", "TSE", "atual", _TSE.format(ano=2024), "HEAD"),
    Alvo("tse-candidatos-2022", "TSE", "atual", _TSE.format(ano=2022), "HEAD"),
    # --- fontes das tasks 39 a 45 -------------------------------------------------------------------
    Alvo(
        "comexstat-ultima-atualizacao",
        "Comex Stat",
        "futuro",
        "https://api-comexstat.mdic.gov.br/cities/dates/updated",
    ),
    Alvo(
        "comexstat-municipios",
        "Comex Stat",
        "futuro",
        "https://api-comexstat.mdic.gov.br/tables/cities",
    ),
    Alvo(
        "demas-cnes-leitos",
        "DEMAS",
        "futuro",
        "https://apidadosabertos.saude.gov.br/assistencia-a-saude/cnes-leitos?co_ibge=172100&limit=1",
    ),
    Alvo(
        "demas-especificacao",
        "DEMAS",
        "futuro",
        "https://apidadosabertos.saude.gov.br/static/swagger.json",
    ),
    Alvo(
        "inep-ideb-2025",
        "Inep",
        "futuro",
        f"{_INEP}/ideb/resultados/divulgacao_anos_iniciais_municipios_2025.zip",
        "HEAD",
    ),
    Alvo(
        "inep-censo-escolar-2024",
        "Inep",
        "futuro",
        f"{_INEP}/dados_abertos/microdados_censo_escolar_2024.zip",
        "HEAD",
    ),
    Alvo(
        "inep-rendimento-2024",
        "Inep",
        "futuro",
        f"{_INEP}/informacoes_estatisticas/indicadores_educacionais/2024/tx_rend_municipios_2024.zip",
        "HEAD",
    ),
    Alvo(
        "tesouro-transparente-capag",
        "Tesouro Transparente",
        "futuro",
        "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=capag-municipios",
    ),
    Alvo(
        "cgu-transferencias",
        "CGU",
        "futuro",
        "https://api.portaldatransparencia.gov.br/api-de-dados/transferencias?pagina=1",
        esperado_401=True,
    ),
    Alvo(
        "pdet-novo-caged",
        "PDET",
        "futuro",
        "ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED/2026/",
        "FTP",
    ),
    Alvo("datasus-sim-obitos", "DATASUS", "futuro", f"{_DATASUS}/SIM/CID10/DORES/", "FTP"),
    Alvo("datasus-cnes-leitos", "DATASUS", "futuro", f"{_DATASUS}/CNES/200508_/Dados/LT/", "FTP"),
]


def classificar(status: int | None, erro: BaseException | None, alvo: Alvo) -> tuple[str, bool]:
    """(classe, acessivel). Acessível = o servidor respondeu de forma utilizável (200 a 399, ou 401 esperado)."""
    if erro is None:
        if status is None:
            return "erro_inesperado", False
        if 200 <= status < 400:
            return "ok", True
        if status == 401 and alvo.esperado_401:
            return "ok_requer_chave", True
        if 400 <= status < 500:
            return "erro_http_4xx", False
        if status >= 500:
            return "erro_servidor_5xx", False
        return "erro_inesperado", False
    if isinstance(erro, ssl.SSLError | ssl.CertificateError | urllib3.exceptions.SSLError):
        return "falha_tls", False
    # Ordem importa: no urllib3, NewConnectionError descende de ConnectTimeoutError (e de TimeoutError),
    # então "conexão recusada" e "DNS" precisam ser testados ANTES de timeout.
    if isinstance(erro, urllib3.exceptions.NameResolutionError | socket.gaierror):
        return "falha_dns", False
    if isinstance(erro, urllib3.exceptions.NewConnectionError):
        return "falha_conexao", False
    if isinstance(erro, urllib3.exceptions.TimeoutError | TimeoutError):
        return "timeout", False
    if isinstance(erro, ftplib.Error):
        return "erro_ftp", False
    if isinstance(erro, urllib3.exceptions.ProtocolError | EOFError | OSError):
        return "falha_conexao", False
    return "erro_inesperado", False


def _desembrulhar(erro: BaseException) -> BaseException:
    """MaxRetryError só embrulha a causa real (TLS, timeout, conexão)."""
    while isinstance(erro, urllib3.exceptions.MaxRetryError) and isinstance(
        erro.reason, BaseException
    ):
        erro = erro.reason
    return erro


def _resumir_erro(erro: BaseException | None) -> str | None:
    if erro is None:
        return None
    return f"{type(erro).__name__}: {erro}".replace("\n", " ")[:TAM_MAX_ERRO]


def _pool(timeout: float) -> urllib3.PoolManager:
    # Sem nova tentativa em erro (a sonda mede a 1ª resposta); segue até 3 redirecionamentos.
    return urllib3.PoolManager(
        ssl_context=_contexto_tls(),
        timeout=urllib3.Timeout(connect=timeout, read=timeout),
        retries=Retry(total=None, connect=0, read=0, redirect=3, status=0, other=0),
    )


def _requisitar(http: Any, metodo: str, url: str) -> int:
    resp = http.request(
        metodo, url, headers={"User-Agent": USER_AGENT_OFICIAL}, preload_content=False
    )
    try:
        return resp.status
    finally:
        resp.close()  # fecha sem baixar o corpo (há zips de 60 MB)


def _registro(alvo: Alvo, protocolo: str, inicio: float, **campos: Any) -> dict[str, Any]:
    status, erro = campos.get("status_code"), campos.pop("erro_obj", None)
    # FTP não tem código de status: listar o diretório sem erro já é "ok"
    classe, acessivel = (
        ("ok", True) if (protocolo == "ftp" and erro is None) else classificar(status, erro, alvo)
    )
    tls_ok = None
    if protocolo == "https":
        tls_ok = True if status is not None else (False if classe == "falha_tls" else None)
    return {
        "id": alvo.id,
        "fonte": alvo.fonte,
        "uso": alvo.uso,
        "url": alvo.url,
        "protocolo": protocolo,
        "metodo": alvo.metodo,
        "status_code": status,
        "latencia_ms": round((perf_counter() - inicio) * 1000),
        "tls_ok": tls_ok,
        "acessivel": acessivel,
        "classe": classe,
        "erro": _resumir_erro(erro),
        "detalhe": campos.get("detalhe"),
    }


def _sondar_http(alvo: Alvo, http: Any) -> dict[str, Any]:
    inicio, status, erro = perf_counter(), None, None
    try:
        status = _requisitar(http, alvo.metodo, alvo.url)
        if alvo.metodo == "HEAD" and status in (405, 501):  # servidor não aceita HEAD
            status = _requisitar(http, "GET", alvo.url)
    except Exception as e:  # a sonda nunca levanta: o erro vira classe no relatório
        erro = _desembrulhar(e)
    return _registro(alvo, urlsplit(alvo.url).scheme, inicio, status_code=status, erro_obj=erro)


def _sondar_ftp(alvo: Alvo, timeout: float, fabrica: Any) -> dict[str, Any]:
    partes = urlsplit(alvo.url)
    inicio, erro, detalhe, ftp = perf_counter(), None, None, None
    try:
        ftp = fabrica(partes.hostname, timeout=timeout)
        ftp.login()  # anônimo
        detalhe = f"{len(ftp.nlst(unquote(partes.path) or '/'))} entradas"
    except Exception as e:  # a sonda nunca levanta
        erro = e
    finally:
        if ftp is not None:
            try:
                ftp.quit()
            except Exception:
                ftp.close()
    return _registro(alvo, "ftp", inicio, erro_obj=erro, detalhe=detalhe)


def sondar(
    alvo: Alvo, timeout: float = 15.0, http: Any = None, fabrica_ftp: Any = ftplib.FTP
) -> dict[str, Any]:
    if alvo.metodo == "FTP":
        return _sondar_ftp(alvo, timeout, fabrica_ftp)
    return _sondar_http(alvo, http or _pool(timeout))


def executar(
    alvos: list[Alvo] | None = None,
    timeout: float = 15.0,
    origem: str = "local",
    http: Any = None,
    fabrica_ftp: Any = ftplib.FTP,
) -> dict[str, Any]:
    alvos = list(ALVOS if alvos is None else alvos)
    ids = [a.id for a in alvos]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    if repetidos:
        raise ValueError(f"ids repetidos na lista de alvos: {repetidos}")
    http = http or _pool(timeout)
    resultados = [sondar(a, timeout, http, fabrica_ftp) for a in alvos]
    return {
        "gerado_em": datetime.now(UTC).isoformat(),
        "origem": origem,
        "timeout_s": timeout,
        "python": platform.python_version(),
        "resumo": {
            "total": len(resultados),
            "acessiveis": sum(r["acessivel"] for r in resultados),
            "por_classe": dict(Counter(r["classe"] for r in resultados)),
        },
        "resultados": resultados,
    }


def comparar(base: dict[str, Any], atual: dict[str, Any]) -> dict[str, Any]:
    """Cruza o relatório de referência (ex.: o computador local) com o atual (ex.: o runner do GitHub)."""
    b = {r["id"]: r for r in base["resultados"]}
    a = {r["id"]: r for r in atual["resultados"]}
    itens = []
    for id_ in [*a, *(i for i in b if i not in a)]:
        rb, ra = b.get(id_), a.get(id_)
        if rb is None or ra is None:
            comp = "sem_par"
        elif rb["acessivel"] and ra["acessivel"]:
            comp = "ok_nos_dois"
        elif rb["acessivel"]:
            comp = "bloqueio_rede_runner"
        elif ra["acessivel"]:
            comp = "so_acessivel_no_runner"
        else:
            comp = "inacessivel_nos_dois"
        ref = ra or rb
        itens.append(
            {
                "id": id_,
                "fonte": ref["fonte"],
                "uso": ref["uso"],
                "classe_base": rb["classe"] if rb else None,
                "classe_atual": ra["classe"] if ra else None,
                "comparacao": comp,
            }
        )
    return {
        "origem_base": base.get("origem"),
        "origem_atual": atual.get("origem"),
        "itens": itens,
        "resumo": dict(Counter(i["comparacao"] for i in itens)),
    }


def resumo_markdown(relatorio: dict[str, Any], comparacao: dict[str, Any] | None = None) -> str:
    """Tabela para o resumo da execução no GitHub (e para colar na spec)."""
    comp = {i["id"]: i for i in comparacao["itens"]} if comparacao else {}
    r = relatorio["resumo"]
    linhas = [
        f"### Sonda de alcance — origem: {relatorio['origem']}",
        f"{r['acessiveis']} de {r['total']} acessíveis · gerado em {relatorio['gerado_em']}",
        "",
        "| Alvo | Fonte | Uso | Resultado | Latência (ms) |"
        + (" Referência | Comparação |" if comp else ""),
        "|---|---|---|---|---|" + ("---|---|" if comp else ""),
    ]
    for x in relatorio["resultados"]:
        status = f" ({x['status_code']})" if x["status_code"] else ""
        linha = f"| {x['id']} | {x['fonte']} | {x['uso']} | {x['classe']}{status} | {x['latencia_ms']} |"
        if comp:
            c = comp.get(x["id"], {})
            linha += f" {c.get('classe_base') or '-'} | {c.get('comparacao', '-')} |"
        linhas.append(linha)
    return "\n".join(linhas) + "\n"
