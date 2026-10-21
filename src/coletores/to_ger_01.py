"""Coletor TO-GER-01 (TSE Dados Abertos — titular eleito: 139 prefeitos + governador TO)."""

from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.http import ClienteHTTP
from src.coletor_base.validacao import validar_titulares
from src.coletores.depara_tse_ibge import DEPARA_TSE_IBGE
from src.coletores.tse_candidatos import baixar_titulares, ler_titulares, montar_registro


class ColetorTOGER01(ColetorBase):
    id_fonte, id_indicador = "TO-GER-01", "titular_eleito"
    tabela_destino, chave_merge = "dim_titular", "id_titular"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-GER-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        return baixar_titulares(ClienteHTTP(delay_segundos=10.0))  # Crawl-Delay: 10 (robots TSE)

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        agora = datetime.now(UTC).isoformat()
        return [
            montar_registro(r, DEPARA_TSE_IBGE.get(r["SG_UE"]), agora, self.id_fonte)
            for r in ler_titulares(bruto)
        ]

    def validar(self, registros: list[dict[str, Any]]) -> None:
        validar_titulares(registros, set(DEPARA_TSE_IBGE.values()))
