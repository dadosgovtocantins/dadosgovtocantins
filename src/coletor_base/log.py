"""
Módulo de log estruturado em JSON para o Cloud Logging.
PRD v4.2 §11.3.
"""

import json
import sys
from datetime import UTC, datetime
from typing import Any


def emitir_log(
    id_execucao: str,
    id_fonte: str,
    id_indicador: str,
    status: str,
    linhas_processadas: int = 0,
    municipios_cobertos: int = 0,
    duracao_ms: int = 0,
    bytes_processados: int = 0,
    hash_origem: str = "",
    erro: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Emite log estruturado em JSON no stdout conforme padronização da seção 11.3 do PRD.
    """
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "id_execucao": id_execucao,
        "id_fonte": id_fonte,
        "id_indicador": id_indicador,
        "status": status,
        "linhas_processadas": linhas_processadas,
        "municipios_cobertos": municipios_cobertos,
        "duracao_ms": duracao_ms,
        "bytes_processados": bytes_processados,
        "hash_origem": hash_origem,
        "erro": erro,
    }
    if kwargs:
        payload["extras"] = kwargs

    # Emite no stdout (canal capturado nativamente pelo Cloud Run Logging)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return payload
