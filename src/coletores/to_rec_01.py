"""Coletor TO-REC-01 (Transferegov Convênios 139 municípios TO) <= 50 linhas."""

import json
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ColetaNaoImplementadaError


class ColetorTOREC01(ColetorBase):
    id_fonte = "TO-REC-01"
    id_indicador = "convenios_transferegov"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-REC-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        raise ColetaNaoImplementadaError(
            f"{self.id_fonte}: coleta real (Transferegov) ainda não implementada; nenhum valor é gerado."
        )

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        payload = json.loads(bruto.decode("utf-8"))
        ano, dt = payload["periodo"], datetime.now(UTC).isoformat()
        return [
            {
                "id_registro": f"convenios_transferegov:TO:{m['id_municipio']}:{ano}",
                "id_indicador": self.id_indicador,
                "id_orgao": "MGI",
                "id_municipio": m["id_municipio"],
                "periodo_ref": f"{ano}-01-01",
                "periodicidade": "Anual",
                "valor_num": float(m["valor_convenios_brl"]),
                "valor_texto": None,
                "unidade": "BRL",
                "id_fonte": self.id_fonte,
                "esfera_fonte": "federal",
                "dt_coleta": dt,
                "qualidade": "ok",
                "calculado": False,
                "gerado_por_ia": False,
            }
            for m in payload["resultados"]
        ]
