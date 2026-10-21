"""
TLS do ClienteHTTP (Task 28): verificação sempre ligada, com o intermediário da Sectigo que o IBGE não envia.
"""

import hashlib
import re
import ssl

from src.coletor_base.http import INTERMEDIARIOS, ClienteHTTP, _contexto_tls

# SHA-256 do "Sectigo Public Server Authentication CA DV R36" (AIA do certificado de *.ibge.gov.br).
SHA256_ESPERADO = "8C54C334B66BA4E426772AF4A3F9136C19A1AEC729FDB28C535C07A5A4EF22E0"


def _certificados() -> list[bytes]:
    pem = INTERMEDIARIOS.read_text("utf-8")
    blocos = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", pem, re.S)
    return [ssl.PEM_cert_to_DER_cert(b) for b in blocos]


def test_intermediario_e_o_certificado_esperado_e_unico():
    """Impede a troca acidental do arquivo: um único certificado, com a impressão digital fixada."""
    certificados = _certificados()
    assert len(certificados) == 1
    assert hashlib.sha256(certificados[0]).hexdigest().upper() == SHA256_ESPERADO


def test_contexto_tls_exige_certificado_e_nome_do_host():
    contexto = _contexto_tls()
    assert contexto.verify_mode == ssl.CERT_REQUIRED
    assert contexto.check_hostname is True


def test_cliente_http_usa_o_contexto_verificado():
    contexto = ClienteHTTP(delay_segundos=0).http.connection_pool_kw["ssl_context"]
    assert contexto.verify_mode == ssl.CERT_REQUIRED and contexto.check_hostname


def test_arquivo_do_intermediario_carrega_no_contexto():
    """PEM corrompido faria _contexto_tls() levantar erro e nenhuma coleta rodaria."""
    assert _contexto_tls().cert_store_stats()["x509_ca"] >= 1
