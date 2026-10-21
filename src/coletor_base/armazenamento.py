"""
Módulo de armazenamento e deduplicação da zona bruta (raw).
PRD v4.2 §1.3 (RF-61, RF-62).
"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path


def calcular_hash_sha256(conteudo: bytes) -> str:
    """Calcula o hash SHA-256 do payload bruto."""
    return hashlib.sha256(conteudo).hexdigest()


class GerenciadorArmazenamentoRaw:
    """
    Gerencia o armazenamento imutável dos arquivos brutos no Cloud Storage / local.
    """

    def __init__(self, bucket_name: str = "dadosgov-raw", diretorio_local: Path | None = None):
        self.bucket_name = bucket_name
        self.diretorio_local = diretorio_local or Path(".data_raw")
        self.diretorio_local.mkdir(parents=True, exist_ok=True)
        self._hash_store_file = self.diretorio_local / "hashes_processados.txt"

    def hash_ja_processado(self, id_fonte: str, hash_sha256: str) -> bool:
        """
        Verifica se o hash SHA-256 já foi processado anteriormente para esta fonte (RF-62).
        """
        if not self._hash_store_file.exists():
            return False

        chave_busca = f"{id_fonte}:{hash_sha256}"
        with open(self._hash_store_file, encoding="utf-8") as f:
            for linha in f:
                if linha.strip() == chave_busca:
                    return True
        return False

    def registrar_hash_processado(self, id_fonte: str, hash_sha256: str) -> None:
        """Registra o hash SHA-256 para evitar reprocessamento idêntico."""
        chave = f"{id_fonte}:{hash_sha256}"
        with open(self._hash_store_file, "a", encoding="utf-8") as f:
            f.write(f"{chave}\n")

    def salvar_raw(
        self, id_fonte: str, conteudo: bytes, hash_sha256: str, extensao: str = "json"
    ) -> str:
        """
        Salva o arquivo bruto imutável (RF-61).
        Retorna o URI do objeto salvo (ex: gs://... ou path local).
        """
        hoje = datetime.now(UTC).strftime("%Y-%m-%d")
        nome_arquivo = f"{hash_sha256}.{extensao}"

        # Salvamento local em ambiente dev/mock
        pasta_destino = self.diretorio_local / id_fonte / hoje
        pasta_destino.mkdir(parents=True, exist_ok=True)
        caminho_arquivo = pasta_destino / nome_arquivo

        if caminho_arquivo.exists():
            # Tentar sobrescrever lança aviso/exceção de imutabilidade se já existir
            return f"file://{caminho_arquivo.resolve()}"

        with open(caminho_arquivo, "wb") as f:
            f.write(conteudo)

        self.registrar_hash_processado(id_fonte, hash_sha256)
        return f"file://{caminho_arquivo.resolve()}"
