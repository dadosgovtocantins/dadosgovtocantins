"""
Módulo de carga idempotente via MERGE no BigQuery / Storage local.
PRD v4.2 §1.3 (RF-67, RF-91).
"""

from typing import Any


class CarregadorBigQuery:
    """
    Gerencia a carga idempotente via MERGE por id_registro.
    """

    def __init__(self, ambiente: str = "dev", maximum_bytes_billed: int = 1_000_000_000):
        self.ambiente = ambiente
        self.maximum_bytes_billed = maximum_bytes_billed
        self._mock_db: dict[str, dict[str, Any]] = {}  # fato_indicador (padrão)
        self._mock_tabelas: dict[str, dict[str, dict[str, Any]]] = {"fato_indicador": self._mock_db}

    def carregar_merge(
        self,
        registros: list[dict[str, Any]],
        tabela: str = "fato_indicador",
        chave: str = "id_registro",
    ) -> int:
        """
        Executa MERGE por `chave` na `tabela` de destino garantindo idempotência (RF-67).
        Padrão: fato_indicador por id_registro. Dimensões (ex: dim_titular) informam a sua.
        Retorna a quantidade de registros inseridos/atualizados.
        """
        if not registros:
            return 0

        # Em ambiente local / dev sem BigQuery ativo, simula a idempotência no dict local
        destino = self._mock_tabelas.setdefault(tabela, {})
        for r in registros:
            destino[str(r[chave])] = r

        return len(registros)

    def obter_validos_por_fonte(self, tabela: str, id_fonte: str) -> list[dict[str, Any]]:
        """
        Recupera todas as linhas válidas gravadas por uma fonte numa tabela de dimensão,
        para preservá-las com qualidade='defasado' em caso de falha (RF-66).
        """
        return [
            r
            for r in self._mock_tabelas.get(tabela, {}).values()
            if r.get("id_fonte") == id_fonte and r.get("qualidade") in ("ok", "defasado")
        ]

    def obter_ultimo_valor_valido(
        self, id_indicador: str, id_municipio: str | None = None
    ) -> dict[str, Any] | None:
        """
        Recupera o último valor válido gravado para preservar o valor com qualidade='defasado' (RF-66).
        """
        candidatos = [
            r
            for r in self._mock_db.values()
            if r.get("id_indicador") == id_indicador
            and r.get("id_municipio") == id_municipio
            and r.get("qualidade") in ("ok", "estimado", "defasado")
        ]
        if not candidatos:
            return None

        # Ordenar por periodo_ref descendente
        candidatos.sort(key=lambda x: str(x.get("periodo_ref")), reverse=True)
        return candidatos[0]
