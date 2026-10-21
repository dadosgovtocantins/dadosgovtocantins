"""Base comum dos coletores IBGE/SIDRA (Task 28): monta a URL, lê a resposta e converte as séries.

Marcações do IBGE: "-" é zero absoluto; "...", "..", "X" e vazio são dado ausente.
Dado ausente nunca vira zero (RF-55): fica de fora e não gera registro.
"""

import json
import math
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.coletor_base.base import ColetorBase
from src.coletor_base.excecoes import ValidacaoError
from src.coletor_base.http import ClienteHTTP

URL_BASE = "https://servicodados.ibge.gov.br/api/v3/agregados"


def _numero(valor: Any) -> float | None:
    if valor == "-":
        return 0.0
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def ler_series(bruto: bytes) -> list[tuple[str, str, float]]:
    """Lê a resposta SIDRA e devolve (id_localidade, periodo, valor), sem os dados ausentes."""
    try:
        resultados = json.loads(bruto.decode("utf-8"))[0]["resultados"]
        if len(resultados) != 1:
            raise ValidacaoError(f"SIDRA devolveu {len(resultados)} resultados; esperado 1.")
        return [
            (str(s["localidade"]["id"]), str(periodo), n)
            for s in resultados[0]["series"]
            for periodo, v in s["serie"].items()
            if (n := _numero(v)) is not None
        ]
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as e:
        raise ValidacaoError(f"Resposta SIDRA em formato inesperado: {e!r}") from e


def periodo_ref(periodo: str) -> str:
    """'2023' -> '2023-01-01'; trimestre AAAAQQ ('202602') -> '2026-04-01'."""
    if len(periodo) == 6:
        return f"{periodo[:4]}-{(int(periodo[4:]) - 1) * 3 + 1:02d}-01"
    return f"{periodo[:4]}-01-01"


class ColetorSidra(ColetorBase):
    """Subclasses declaram só agregado, variável, períodos e unidade."""

    agregado: ClassVar[str]
    variavel: ClassVar[str]
    periodos: ClassVar[str]
    unidade: ClassVar[str]
    localidades: ClassVar[str] = "N6[N3[17]]"  # 139 municípios do TO; "N3[17]" = estado
    classificacao: ClassVar[str] = ""
    periodicidade: ClassVar[str] = "Anual"
    id_orgao: ClassVar[str] = "IBGE"

    def url(self) -> str:
        url = f"{URL_BASE}/{self.agregado}/periodos/{self.periodos}/variaveis/{self.variavel}"
        url += f"?localidades={self.localidades}"
        return url + (f"&classificacao={self.classificacao}" if self.classificacao else "")

    def extrair(self) -> bytes:
        return ClienteHTTP().get(self.url())

    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        dt = datetime.now(UTC).isoformat()
        municipal = self.localidades.startswith("N6")
        registros = []
        for loc, periodo, valor in ler_series(bruto):
            chave = f"{loc}:" if municipal else ""
            registros.append(
                {
                    "id_registro": f"{self.id_indicador}:TO:{chave}{periodo}",
                    "id_indicador": self.id_indicador,
                    "id_orgao": self.id_orgao,
                    "id_municipio": loc if municipal else None,
                    "periodo_ref": periodo_ref(periodo),
                    "periodicidade": self.periodicidade,
                    "valor_num": valor,
                    "valor_texto": f"{int(periodo[4:])}T{periodo[:4]}"
                    if len(periodo) == 6
                    else None,
                    "unidade": self.unidade,
                    "id_fonte": self.id_fonte,
                    "esfera_fonte": "federal",
                    "dt_coleta": dt,
                    "qualidade": "ok",
                    "calculado": False,
                    "gerado_por_ia": False,
                }
            )
        return registros
