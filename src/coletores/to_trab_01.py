"""Coletor TO-TRAB-01 (Novo CAGED - Saldo de Emprego 139 municípios TO) <= 50 linhas."""

import json
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ColetaNaoImplementadaError


class ColetorTOTRAB01(ColetorBase):
    id_fonte = "TO-TRAB-01"
    id_indicador = "saldo_emprego_caged"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TRAB-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        raise ColetaNaoImplementadaError(
            f"{self.id_fonte}: coleta real (Novo CAGED) ainda não implementada; nenhum valor é gerado."
        )

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        payload = json.loads(bruto.decode("utf-8"))
        periodo, dt = payload["periodo"], datetime.now(UTC).isoformat()
        return [
            {
                "id_registro": f"saldo_emprego_caged:TO:{m['id_municipio']}:{periodo}",
                "id_indicador": self.id_indicador,
                "id_orgao": "MTE",
                "id_municipio": m["id_municipio"],
                "periodo_ref": periodo,
                "periodicidade": "Mensal",
                "valor_num": float(m["saldo_movimentacao"]),
                "valor_texto": None,
                "unidade": "postos",
                "id_fonte": self.id_fonte,
                "esfera_fonte": "federal",
                "dt_coleta": dt,
                "qualidade": "ok",
                "calculado": False,
                "gerado_por_ia": False,
            }
            for m in payload["resultados"]
        ]
