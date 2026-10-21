"""
Guarda de conformidade de coleta (robots.txt e termos de uso).
PRD v4.2 §1.3 (RF-71) e §12.3.
"""

from typing import Any

from src.coletor_base.excecoes import ColetaBloqueadaError


def checar_conformidade_coleta(metadata_fonte: dict[str, Any]) -> None:
    """
    Verifica se a fonte possui restrição no robots.txt ou nos termos de uso.
    Se a coluna 'RESTRIÇÃO ROBOTS/TERMOS' indicar bloqueio (ex: inicia com 'Sim'),
    lança ColetaBloqueadaError imediatamente antes de abrir qualquer conexão de rede.
    """
    restricao = str(metadata_fonte.get("RESTRIÇÃO ROBOTS/TERMOS", "")).strip()

    if restricao.lower().startswith("sim"):
        fonte_id = metadata_fonte.get("ID", "desconhecido")
        raise ColetaBloqueadaError(
            f"Fonte '{fonte_id}' possui restrição registrada em robots.txt/termos: '{restricao}'. "
            f"Coleta interrompida por design (RF-71)."
        )
