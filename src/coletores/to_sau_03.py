"""Coletor TO-SAU-03 (SIM/SINASC Mortalidade Infantil 139 municípios TO) <= 50 linhas."""

import json
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ColetaNaoImplementadaError


class ColetorTOSAU03(ColetorBase):
    id_fonte = "TO-SAU-03"
    id_indicador = "mortalidade_infantil"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-SAU-03",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        raise ColetaNaoImplementadaError(
            f"{self.id_fonte}: coleta real (SIM/SINASC) ainda não implementada; nenhum valor é gerado."
        )

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        payload = json.loads(bruto.decode("utf-8"))
        ano, dt = payload["periodo"], datetime.now(UTC).isoformat()
        return [
            {
                "id_registro": f"mortalidade_infantil:TO:{m['id_municipio']}:{ano}",
                "id_indicador": self.id_indicador,
                "id_orgao": "DATASUS",
                "id_municipio": m["id_municipio"],
                "periodo_ref": f"{ano}-01-01",
                "periodicidade": "Anual",
                "valor_num": float(m["taxa_mortalidade_infantil"]),
                "valor_texto": None,
                "unidade": "óbitos/mil nascidos",
                "id_fonte": self.id_fonte,
                "esfera_fonte": "federal",
                "dt_coleta": dt,
                "qualidade": "ok",
                "calculado": False,
                "gerado_por_ia": False,
            }
            for m in payload["resultados"]
        ]
