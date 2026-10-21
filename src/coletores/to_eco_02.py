"""Coletor TO-ECO-02 (Mapa de Empresas - Empresas Ativas 139 municípios TO) <= 50 linhas."""

import json
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ColetaNaoImplementadaError


class ColetorTOECO02(ColetorBase):
    id_fonte = "TO-ECO-02"
    id_indicador = "empresas_ativas"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-ECO-02",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        raise ColetaNaoImplementadaError(
            f"{self.id_fonte}: coleta real (Mapa de Empresas) ainda não implementada; nenhum valor é gerado."
        )

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        payload = json.loads(bruto.decode("utf-8"))
        periodo, dt = payload["periodo"], datetime.now(UTC).isoformat()
        return [
            {
                "id_registro": f"empresas_ativas:TO:{m['id_municipio']}:{periodo}",
                "id_indicador": self.id_indicador,
                "id_orgao": "ME",
                "id_municipio": m["id_municipio"],
                "periodo_ref": periodo,
                "periodicidade": "Quadrimestral",
                "valor_num": float(m["qtd_empresas_ativas"]),
                "valor_texto": None,
                "unidade": "empresas",
                "id_fonte": self.id_fonte,
                "esfera_fonte": "federal",
                "dt_coleta": dt,
                "qualidade": "ok",
                "calculado": False,
                "gerado_por_ia": False,
            }
            for m in payload["resultados"]
        ]
