"""
Cliente HTTP do framework ColetorBase.
PRD v4.2 §12.3 e Task 06 (User-Agent público e rate limit auto-imposto).
"""

import ssl
import time
from pathlib import Path

import certifi
import urllib3
from urllib3.util import Retry

USER_AGENT_OFICIAL = (
    "PainelTOEmDados/1.0 (Unitins PIBIEX Extension Project; "
    "https://github.com/unitins/painel-to-em-dados; contato.painelto@unitins.br)"
)
# Intermediário público que o servicodados.ibge.gov.br deixou de enviar (ver o cabeçalho do arquivo).
INTERMEDIARIOS = Path(__file__).parent / "certs" / "sectigo_dv_r36.pem"


def _contexto_tls() -> ssl.SSLContext:
    """Verificação TLS completa (certificado e nome do host) com as raízes do certifi, como o requests faz.

    O Python do sistema pode não confiar na cadeia do IBGE; o intermediário fornecido só completa o elo
    que o servidor não envia: ele próprio é assinado por uma raiz do certifi, então não amplia a confiança.
    """
    contexto = ssl.create_default_context(cafile=certifi.where())
    contexto.load_verify_locations(cafile=str(INTERMEDIARIOS))
    return contexto


class ClienteHTTP:
    """
    Cliente HTTP seguro com User-Agent identificado, rate limit auto-imposto e retries.
    """

    def __init__(self, delay_segundos: float = 1.0, max_retries: int = 3):
        self.delay_segundos = delay_segundos
        self.user_agent = USER_AGENT_OFICIAL

        retries = Retry(
            total=max_retries,
            backoff_factor=1.5,
            status_forcelist=[500, 502, 503, 504],
        )
        self.http = urllib3.PoolManager(
            retries=retries,
            ssl_context=_contexto_tls(),
            timeout=urllib3.Timeout(connect=10, read=60),
        )

    def get(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        """
        Realiza requisição GET com rate limit auto-imposto e User-Agent oficial.
        """
        # Rate limit auto-imposto entre requisições
        if self.delay_segundos > 0:
            time.sleep(self.delay_segundos)

        req_headers: dict[str, str] = {"User-Agent": self.user_agent}
        if headers:
            req_headers.update(headers)

        res = self.http.request("GET", url, headers=req_headers)
        if res.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP GET falhou com status {res.status} em {url}")

        return res.data
