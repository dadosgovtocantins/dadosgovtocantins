"""Coletor TO-GER-02 (DivulgaCandContas — retrato do titular eleito) — BLOQUEADO por RF-71."""

from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ColetaBloqueadaError

# Verificado em 2026-10-14: GET https://divulgacandcontas.tse.jus.br/robots.txt → 403 "Access Denied"
# (WAF Akamai). Sem robots/termos confirmáveis e com bloqueio ativo de acesso automatizado, a
# fonte entra como LINK, não como dado (RF-71). url_foto em dim_titular permanece NULL.
LINK_PUBLICO = "https://divulgacandcontas.tse.jus.br/divulga/"
MOTIVO = (
    "Sim — WAF bloqueia acesso automatizado (robots.txt 403 em 2026-10-14); fonte entra como link"
)


class ColetorTOGER02(ColetorBase):
    id_fonte, id_indicador = "TO-GER-02", "retrato_titular"
    tabela_destino, chave_merge = "dim_titular", "id_titular"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-GER-02",
        "RESTRIÇÃO ROBOTS/TERMOS": MOTIVO,
    }

    def extrair(self) -> bytes:
        # Nunca alcançado via executar(): a guarda de conformidade barra antes. Defesa em profundidade.
        raise ColetaBloqueadaError(f"{self.id_fonte}: {MOTIVO}. Consulte {LINK_PUBLICO}")

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        raise ColetaBloqueadaError(f"{self.id_fonte}: {MOTIVO}. Nenhum retrato é gravado.")
