"""
Sonda de alcance (Task 35, passo 1): src/orquestracao/alcance.py e scripts/testar_alcance.py.

Sem internet: um servidor HTTP local reproduz 200, 401, 403, 404, 500, HEAD não permitido, lentidão e
redirecionamento; o FTP é simulado; a conexão recusada usa uma porta fechada.
"""

import importlib.util
import json
import socket
import ssl
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest
import urllib3
from src.orquestracao import alcance
from src.orquestracao.alcance import Alvo

RAIZ = Path(__file__).parents[2]
CAMPOS = {
    "id",
    "fonte",
    "uso",
    "url",
    "protocolo",
    "metodo",
    "status_code",
    "latencia_ms",
    "tls_ok",
    "acessivel",
    "classe",
    "erro",
    "detalhe",
    "tentativas",
}


class Manipulador(BaseHTTPRequestHandler):
    pedidos: ClassVar[Counter] = Counter()

    def log_message(self, *args):  # silencia o log do servidor de teste
        pass

    def _responder(self, metodo: str):
        caminho = self.path.split("?")[0]
        self.pedidos[caminho] += 1
        if caminho == "/reseta-uma-vez" and self.pedidos[caminho] == 1:
            self.close_connection = True  # sem resposta: o cliente vê a conexão derrubada (reset)
            return
        if caminho == "/lento":
            threading.Event().wait(2.0)
        if caminho == "/redireciona":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        if caminho == "/head405" and metodo == "HEAD":
            self.send_response(405)
            self.end_headers()
            return
        codigo = {"/403": 403, "/401": 401, "/404": 404, "/500": 500}.get(caminho, 200)
        corpo = b'{"ok": true}'
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        if metodo != "HEAD":
            self.wfile.write(corpo)

    def do_GET(self):
        self._responder("GET")

    def do_HEAD(self):
        self._responder("HEAD")


@pytest.fixture(scope="module")
def servidor():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _alvo(url, **extra):
    return Alvo(id="t/" + url[-12:], fonte="Teste", uso="atual", url=url, **extra)


def _porta_fechada() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# --- classificação -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "erro", "esperado"),
    [
        (200, None, ("ok", True)),
        (204, None, ("ok", True)),
        (302, None, ("ok", True)),
        (403, None, ("erro_http_4xx", False)),
        (404, None, ("erro_http_4xx", False)),
        (429, None, ("erro_http_4xx", False)),
        (500, None, ("erro_servidor_5xx", False)),
        (503, None, ("erro_servidor_5xx", False)),
        (None, urllib3.exceptions.SSLError("handshake"), ("falha_tls", False)),
        (None, ssl.SSLCertVerificationError("cadeia incompleta"), ("falha_tls", False)),
        (None, urllib3.exceptions.ConnectTimeoutError(), ("timeout", False)),
        (None, TimeoutError(), ("timeout", False)),
        (None, urllib3.exceptions.NewConnectionError(None, "recusada"), ("falha_conexao", False)),
        (None, ConnectionRefusedError(), ("falha_conexao", False)),
        (
            None,
            urllib3.exceptions.NameResolutionError("exemplo.invalid", None, OSError("sem DNS")),
            ("falha_dns", False),
        ),
        (None, socket.gaierror(-2, "Name or service not known"), ("falha_dns", False)),
        (
            None,
            urllib3.exceptions.ProtocolError("Connection aborted.", ConnectionResetError()),
            ("falha_conexao", False),
        ),
        (None, ValueError("algo inesperado"), ("erro_inesperado", False)),
    ],
)
def test_classificacao(status, erro, esperado):
    assert alcance.classificar(status, erro, _alvo("http://x/")) == esperado


def test_401_so_e_acessivel_quando_a_fonte_exige_chave():
    assert alcance.classificar(401, None, _alvo("http://x/", esperado_401=True)) == (
        "ok_requer_chave",
        True,
    )
    assert alcance.classificar(401, None, _alvo("http://x/")) == ("erro_http_4xx", False)


# --- HTTP contra o servidor local ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("caminho", "metodo", "classe", "status", "acessivel"),
    [
        ("/ok", "GET", "ok", 200, True),
        ("/ok", "HEAD", "ok", 200, True),
        ("/redireciona", "GET", "ok", 200, True),
        ("/head405", "HEAD", "ok", 200, True),  # HEAD recusado → repete com GET
        ("/403", "GET", "erro_http_4xx", 403, False),
        ("/404", "HEAD", "erro_http_4xx", 404, False),
        ("/500", "GET", "erro_servidor_5xx", 500, False),
    ],
)
def test_sondar_http(servidor, caminho, metodo, classe, status, acessivel):
    r = alcance.sondar(_alvo(f"http://{servidor}{caminho}", metodo=metodo), timeout=5)
    assert (r["classe"], r["status_code"], r["acessivel"]) == (classe, status, acessivel)
    assert r["tls_ok"] is None and r["protocolo"] == "http" and r["latencia_ms"] >= 0


def test_401_com_chave_esperada(servidor):
    r = alcance.sondar(_alvo(f"http://{servidor}/401", esperado_401=True), timeout=5)
    assert (r["classe"], r["status_code"], r["acessivel"]) == ("ok_requer_chave", 401, True)


def test_timeout_nao_levanta_excecao(servidor):
    r = alcance.sondar(_alvo(f"http://{servidor}/lento"), timeout=0.4)
    assert r["classe"] == "timeout" and r["acessivel"] is False and r["status_code"] is None
    assert r["latencia_ms"] < 1800  # respeitou o timeout, não esperou os 2 s do servidor


def test_conexao_recusada():
    r = alcance.sondar(_alvo(f"http://127.0.0.1:{_porta_fechada()}/x"), timeout=2)
    assert r["classe"] == "falha_conexao" and r["acessivel"] is False


def test_tls_contra_servidor_sem_tls_reprova_com_tls_ok_falso(servidor):
    r = alcance.sondar(_alvo(f"https://{servidor}/ok"), timeout=3)
    assert r["classe"] == "falha_tls" and r["tls_ok"] is False and r["acessivel"] is False


def test_tls_ok_verdadeiro_quando_a_resposta_chega_por_https():
    class PoolFalso:
        def request(self, metodo, url, **kw):
            return SimpleNamespace(status=200, close=lambda: None, release_conn=lambda: None)

    r = alcance.sondar(_alvo("https://exemplo.invalid/x"), timeout=3, http=PoolFalso())
    assert r["tls_ok"] is True and r["classe"] == "ok" and r["protocolo"] == "https"


def test_erro_vem_resumido_e_sem_quebra_de_linha():
    r = alcance.sondar(_alvo(f"http://127.0.0.1:{_porta_fechada()}/x"), timeout=2)
    assert isinstance(r["erro"], str) and len(r["erro"]) <= 160 and "\n" not in r["erro"]


# --- nova tentativa (1 retry, só em falha_conexao e timeout) -------------------------------------


@pytest.fixture(autouse=True)
def _zera_pedidos():
    Manipulador.pedidos.clear()


def test_reset_passageiro_e_recuperado_na_segunda_tentativa(servidor):
    r = alcance.sondar(_alvo(f"http://{servidor}/reseta-uma-vez"), timeout=3, pausa_s=0)
    assert (r["classe"], r["acessivel"], r["tentativas"]) == ("ok", True, 2)
    assert Manipulador.pedidos["/reseta-uma-vez"] == 2


def test_timeout_e_conexao_recusada_tentam_duas_vezes_e_registram():
    for url, classe in ((f"http://127.0.0.1:{_porta_fechada()}/x", "falha_conexao"),):
        r = alcance.sondar(_alvo(url), timeout=1, pausa_s=0)
        assert (r["classe"], r["tentativas"]) == (classe, 2)


def test_timeout_repetido_conta_duas_tentativas(servidor):
    r = alcance.sondar(_alvo(f"http://{servidor}/lento"), timeout=0.3, pausa_s=0)
    assert (r["classe"], r["tentativas"]) == ("timeout", 2)
    assert Manipulador.pedidos["/lento"] == 2


@pytest.mark.parametrize("caminho", ["/ok", "/403", "/404", "/500"])
def test_resposta_http_nao_repete(servidor, caminho):
    r = alcance.sondar(_alvo(f"http://{servidor}{caminho}"), timeout=3, pausa_s=0)
    assert r["tentativas"] == 1 and Manipulador.pedidos[caminho] == 1


def test_tls_e_dns_nao_repetem(servidor):
    assert alcance.sondar(_alvo(f"https://{servidor}/ok"), timeout=3, pausa_s=0)["tentativas"] == 1


def test_ftp_com_falha_passageira_e_recuperado():
    class FtpInstavel(FtpFalso):
        chamadas: ClassVar[int] = 0

        def __init__(self, host, timeout=None):
            type(self).chamadas += 1
            if type(self).chamadas == 1:
                raise EOFError("conexão encerrada")
            super().__init__(host, timeout)

    r = alcance.sondar(_ftp(), timeout=3, fabrica_ftp=FtpInstavel, pausa_s=0)
    assert (r["classe"], r["tentativas"]) == ("ok", 2)


def test_erro_de_ftp_de_protocolo_nao_repete():
    FtpFalso.falha = __import__("ftplib").error_perm("530 Login incorrect")
    assert alcance.sondar(_ftp(), timeout=3, fabrica_ftp=FtpFalso, pausa_s=0)["tentativas"] == 1


# --- FTP simulado -------------------------------------------------------------------------------


class FtpFalso:
    nomes: ClassVar[list[str]] = ["202607", "202608"]
    falha: ClassVar[BaseException | None] = None

    def __init__(self, host, timeout=None):
        self.host, self.timeout = host, timeout
        if type(self).falha and isinstance(type(self).falha, (TimeoutError, EOFError)):
            raise type(self).falha

    def login(self):
        import ftplib

        if type(self).falha and isinstance(type(self).falha, ftplib.Error):
            raise type(self).falha

    def nlst(self, caminho):
        self.caminho = caminho
        return list(type(self).nomes)

    def quit(self):
        pass

    def close(self):
        pass


def _ftp(url="ftp://ftp.exemplo.invalid/pdet/microdados/NOVO%20CAGED/2026/"):
    return Alvo(id="t/ftp", fonte="PDET", uso="futuro", url=url, metodo="FTP")


@pytest.fixture(autouse=True)
def _ftp_limpo():
    FtpFalso.nomes, FtpFalso.falha = ["202607", "202608"], None


def test_ftp_ok_lista_e_conta():
    r = alcance.sondar(_ftp(), timeout=3, fabrica_ftp=FtpFalso)
    assert (r["classe"], r["acessivel"], r["protocolo"], r["tls_ok"]) == ("ok", True, "ftp", None)
    assert r["detalhe"] == "2 entradas" and r["status_code"] is None


def test_ftp_decodifica_o_caminho():
    capturado = {}

    class Espiao(FtpFalso):
        def nlst(self, caminho):
            capturado["caminho"] = caminho
            return super().nlst(caminho)

    alcance.sondar(_ftp(), timeout=3, fabrica_ftp=Espiao)
    assert capturado["caminho"] == "/pdet/microdados/NOVO CAGED/2026/"


@pytest.mark.parametrize(
    ("falha", "classe"),
    [
        (TimeoutError(), "timeout"),
        (EOFError(), "falha_conexao"),
        (__import__("ftplib").error_perm("530 Login incorrect"), "erro_ftp"),
        (__import__("ftplib").error_temp("421 Muitos usuários"), "erro_ftp"),
    ],
)
def test_ftp_falhas_sao_classificadas_sem_levantar(falha, classe):
    FtpFalso.falha = falha
    r = alcance.sondar(_ftp(), timeout=3, fabrica_ftp=FtpFalso)
    assert r["classe"] == classe and r["acessivel"] is False


# --- relatório ----------------------------------------------------------------------------------


def test_executar_um_alvo_ruim_nao_derruba_os_demais(servidor):
    alvos = [
        _alvo(f"http://{servidor}/ok"),
        _alvo(f"http://{servidor}/403"),
        _alvo(f"http://127.0.0.1:{_porta_fechada()}/x"),
        _ftp(),
    ]
    rel = alcance.executar(alvos, timeout=2, origem="teste", fabrica_ftp=FtpFalso, pausa_s=0)
    assert len(rel["resultados"]) == 4 and rel["origem"] == "teste"
    assert all(set(r) == CAMPOS for r in rel["resultados"])
    assert [r["acessivel"] for r in rel["resultados"]] == [True, False, False, True]
    assert [r["tentativas"] for r in rel["resultados"]] == [
        1,
        1,
        2,
        1,
    ]  # só a conexão recusada repetiu
    assert rel["resumo"]["total"] == 4 and rel["resumo"]["acessiveis"] == 2
    assert rel["resumo"]["por_classe"] == {"ok": 2, "erro_http_4xx": 1, "falha_conexao": 1}
    assert rel["gerado_em"].endswith("+00:00") or rel["gerado_em"].endswith("Z")
    json.dumps(rel)  # serializável


def test_ids_repetidos_sao_recusados():
    with pytest.raises(ValueError, match="repetidos"):
        alcance.executar([_alvo("http://a/x"), _alvo("http://a/x")], timeout=1, origem="t")


# --- comparação entre ambientes -----------------------------------------------------------------


def _rel(**classes):
    return {
        "origem": "x",
        "resultados": [
            {
                "id": i,
                "fonte": "F",
                "uso": "atual",
                "url": "u",
                "classe": c,
                "acessivel": c.startswith("ok"),
            }
            for i, c in classes.items()
        ],
    }


def test_comparar_marca_bloqueio_do_runner():
    base = _rel(a="ok", b="ok", c="erro_http_4xx", d="ok", e="ok")
    atual = _rel(a="ok", b="erro_http_4xx", c="erro_http_4xx", d="timeout", f="ok")
    comp = alcance.comparar(base, atual)
    por_id = {i["id"]: i["comparacao"] for i in comp["itens"]}
    assert por_id == {
        "a": "ok_nos_dois",
        "b": "bloqueio_rede_runner",
        "c": "inacessivel_nos_dois",
        "d": "bloqueio_rede_runner",
        "e": "sem_par",
        "f": "sem_par",
    }
    assert comp["resumo"]["bloqueio_rede_runner"] == 2


def test_comparar_fonte_que_so_funciona_no_runner():
    comp = alcance.comparar(_rel(a="falha_conexao"), _rel(a="ok"))
    assert comp["itens"][0]["comparacao"] == "so_acessivel_no_runner"


# --- lista de alvos -----------------------------------------------------------------------------


def test_alvos_cobrem_as_fontes_atuais_e_as_futuras():
    fontes_atuais = {a.fonte for a in alcance.ALVOS if a.uso == "atual"}
    fontes_futuras = {a.fonte for a in alcance.ALVOS if a.uso == "futuro"}
    assert {"IBGE", "SICONFI", "TSE"} <= fontes_atuais
    assert {
        "Comex Stat",
        "DEMAS",
        "Inep",
        "Tesouro Transparente",
        "CGU",
        "PDET",
        "DATASUS",
    } <= fontes_futuras


def test_alvos_sao_bem_formados():
    ids = [a.id for a in alcance.ALVOS]
    assert len(ids) == len(set(ids)) and len(ids) >= 18
    for a in alcance.ALVOS:
        assert a.uso in {"atual", "futuro"} and a.metodo in {"GET", "HEAD", "FTP"}
        esquema = a.url.split(":", 1)[0]
        assert esquema in {"https", "ftp"}, a.url  # nada em HTTP puro
        assert (esquema == "ftp") == (a.metodo == "FTP")
    assert sum(a.esperado_401 for a in alcance.ALVOS) == 1  # só a API da CGU


def test_alvos_atuais_cobrem_os_agregados_do_ibge_usados_pelos_coletores():
    urls = " ".join(a.url for a in alcance.ALVOS if a.fonte == "IBGE")
    for agregado in ("6579", "5938", "4714", "5457", "3939", "4099"):
        assert f"/agregados/{agregado}/" in urls, agregado


# --- resumo em markdown -------------------------------------------------------------------------


def test_resumo_markdown_tem_uma_linha_por_alvo(servidor):
    alvos = [_alvo(f"http://{servidor}/ok"), _alvo(f"http://{servidor}/403")]
    rel = alcance.executar(alvos, timeout=2, origem="teste")
    md = alcance.resumo_markdown(rel)
    assert md.count("\n| ") >= 3 and "erro_http_4xx" in md and "teste" in md
    md2 = alcance.resumo_markdown(rel, alcance.comparar(rel, rel))
    assert "ok_nos_dois" in md2


# --- linha de comando ---------------------------------------------------------------------------


def _script():
    spec = importlib.util.spec_from_file_location(
        "testar_alcance", RAIZ / "scripts" / "testar_alcance.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_cli_grava_json_resumo_e_compara(servidor, tmp_path, capsys):
    alvos = [_alvo(f"http://{servidor}/ok"), _alvo(f"http://{servidor}/403")]
    saida, base, md = tmp_path / "a.json", tmp_path / "base.json", tmp_path / "r.md"
    base.write_text(json.dumps(alcance.executar(alvos, timeout=2, origem="local")), "utf-8")
    codigo = _script().main(
        [
            "--origem",
            "github-actions",
            "--saida",
            str(saida),
            "--comparar",
            str(base),
            "--resumo-md",
            str(md),
            "--imprimir-json",
            "--timeout",
            "2",
        ],
        alvos=alvos,
    )
    assert codigo == 0  # informativa: endereço inacessível não vira erro
    rel = json.loads(saida.read_text("utf-8"))
    assert rel["origem"] == "github-actions" and rel["comparacao"]["resumo"]["ok_nos_dois"] == 1
    assert "ok_nos_dois" in md.read_text("utf-8")
    texto = capsys.readouterr().out
    assert "BEGIN_ALCANCE_JSON" in texto and "END_ALCANCE_JSON" in texto


def test_cli_recusa_timeout_invalido(capsys):
    with pytest.raises(SystemExit):
        _script().main(["--timeout", "0"], alvos=[])
