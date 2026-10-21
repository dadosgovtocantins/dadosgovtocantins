"""Coletor TO-REC-02 (SICONFI RREO Anexo 3: Receita Corrente Líquida, 139 municípios e estado)."""

from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletores.siconfi import coletar_rcl, ler_itens


class ColetorTOREC02(ColetorBase):
    id_fonte = "TO-REC-02"
    id_indicador = "receita_corrente_liquida"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-REC-02",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def extrair(self) -> bytes:
        return coletar_rcl()

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        dt = datetime.now(UTC).isoformat()
        registros = []
        for i in ler_itens(bruto):
            ente, ano = i["cod_ibge"], i["exercicio"]
            estado = ente == "17"
            registros.append(
                {
                    "id_registro": f"{self.id_indicador}:TO:{'' if estado else ente + ':'}{ano}",
                    "id_indicador": self.id_indicador,
                    "id_orgao": "STN",
                    "id_municipio": None if estado else ente,
                    "periodo_ref": f"{ano}-01-01",
                    "periodicidade": "Anual",
                    "valor_num": i["valor"] / 1000,  # R$ -> R$ mil
                    "valor_texto": None,
                    "unidade": "R$ mil",
                    "id_fonte": self.id_fonte,
                    "esfera_fonte": "federal",
                    "dt_coleta": dt,
                    "qualidade": "ok",
                    "calculado": False,
                    "gerado_por_ia": False,
                }
            )
        return registros
