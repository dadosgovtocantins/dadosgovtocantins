"""
ClienteHTTP e o bloqueio por excesso de consultas (HTTP 429), Task 35 passo 2.
Servidor HTTP local: devolve 429 (com Retry-After) N vezes e depois 200. A internet continua bloqueada nos testes.
"""

import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

import pytest
import urllib3
from src.coletor_base.http import ClienteHTTP
from src.coletores import siconfi

GET_REAL = ClienteHTTP.get  # guardado antes da trava autouse (conftest) que bloqueia a internet


class Manipulador(BaseHTTPRequestHandler):
    pedidos: ClassVar[Counter] = Counter()

    def log_message(self, *args):
        pass

    def _responder(self, codigo: int, retry_after: str | None = None):
        corpo = b'{"ok": true}' if codigo == 200 else b""
        self.send_response(codigo)
        if retry_after is not None:
            self.send_header("Retry-After", retry_after)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        # /limita/<n>/<retry_after>: 429 nas n primeiras vezes e depois 200; /status/<código>: devolve o código
        self.pedidos[self.path] += 1
        _, rota, a, *resto = [*self.path.split("/"), "", ""]
        if rota == "limita" and self.pedidos[self.path] <= int(a):
            return self._responder(429, resto[0])
        return self._responder(int(a) if rota == "status" else 200)


@pytest.fixture(scope="module")
def base():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture(autouse=True)
def _real(monkeypatch):
    Manipulador.pedidos.clear()
    monkeypatch.setattr(
        ClienteHTTP, "get", GET_REAL
    )  # estes testes usam o cliente de verdade, só em 127.0.0.1


def test_429_entra_na_lista_de_tentativas_e_respeita_retry_after():
    r = ClienteHTTP(delay_segundos=0).http.connection_pool_kw["retries"]
    assert 429 in r.status_forcelist and 503 in r.status_forcelist
    assert r.respect_retry_after_header is True and r.retry_after_max <= 120  # nunca espera horas


def test_429_passageiro_e_recuperado(base):
    corpo = ClienteHTTP(delay_segundos=0, backoff_factor=0).get(f"{base}/limita/2/0")
    assert corpo == b'{"ok": true}'
    assert Manipulador.pedidos["/limita/2/0"] == 3  # 2 bloqueios + a resposta boa


def test_429_persistente_falha_depois_das_tentativas_e_nao_devolve_dado(base):
    cliente = ClienteHTTP(delay_segundos=0, max_retries=2, backoff_factor=0)
    with pytest.raises(urllib3.exceptions.MaxRetryError):
        cliente.get(f"{base}/limita/99/0")
    assert Manipulador.pedidos["/limita/99/0"] == 3  # 1 + 2 novas tentativas, nenhuma a mais


def test_retry_after_do_servidor_e_respeitado(base):
    inicio = time.perf_counter()
    ClienteHTTP(delay_segundos=0, backoff_factor=0).get(f"{base}/limita/1/1")
    assert time.perf_counter() - inicio >= 0.9


def test_retry_after_enorme_e_limitado(base):
    inicio = time.perf_counter()
    cliente = ClienteHTTP(delay_segundos=0, max_retries=1, backoff_factor=0, retry_after_max=1)
    cliente.get(
        f"{base}/limita/1/3600"
    )  # o servidor pede 1 hora; o teto manda esperar no máximo 1 s
    assert time.perf_counter() - inicio < 5


def test_404_nao_tenta_de_novo_e_nao_vira_dado(base):
    with pytest.raises(urllib3.exceptions.HTTPError, match="404"):
        ClienteHTTP(delay_segundos=0).get(f"{base}/status/404")
    assert Manipulador.pedidos["/status/404"] == 1


# --- SICONFI: ritmo e tentativas --------------------------------------------------------------------


def test_siconfi_usa_1_segundo_entre_consultas_e_ate_5_tentativas(rede_gravada, monkeypatch):
    capturado = {}
    original = siconfi.ClienteHTTP

    class Espiao(original):
        def __init__(self, **kw):
            capturado.update(kw)
            super().__init__(**kw)

    monkeypatch.setattr(siconfi, "ClienteHTTP", Espiao)
    siconfi.coletar_rcl(exercicios=1)
    assert capturado["delay_segundos"] == 1.0
    assert capturado["max_retries"] == 5
    assert capturado["backoff_factor"] == 2.0
