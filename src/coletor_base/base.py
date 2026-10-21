"""
Classe base abstrata ColetorBase.
PRD v4.2 Anexo D, RNF-E02 e Task 06.
"""

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from src.coletor_base.armazenamento import GerenciadorArmazenamentoRaw, calcular_hash_sha256
from src.coletor_base.carga import CarregadorBigQuery
from src.coletor_base.conformidade import checar_conformidade_coleta
from src.coletor_base.excecoes import FonteIndisponivelError
from src.coletor_base.log import emitir_log
from src.coletor_base.validacao import checar_variacao_3_sigma, validar_registros


class ColetorBase(ABC):
    """
    Contrato padronizado que todos os ~18 coletores herdam (~40 linhas por fonte).
    """

    id_fonte: str
    id_indicador: str
    metadata_fonte: ClassVar[dict[str, Any]] = {}
    # Destino da carga. Padrão: fato_indicador por id_registro. Coletores de dimensão
    # (ex: dim_titular, task 30) declaram a própria tabela e chave — sem sobrescrever executar().
    tabela_destino: ClassVar[str] = "fato_indicador"
    chave_merge: ClassVar[str] = "id_registro"

    def __init__(self, ambiente: str = "dev"):
        self.ambiente = ambiente
        self.armazenamento = GerenciadorArmazenamentoRaw()
        self.carregador = CarregadorBigQuery(ambiente=ambiente)

    @abstractmethod
    def extrair(self) -> bytes:
        """Baixa o conteúdo bruto da origem de dados."""
        pass

    @abstractmethod
    def transformar(self, bruto: bytes) -> list[dict[str, Any]]:
        """Converte o payload bruto no schema da tabela_destino (padrão: fato_indicador)."""
        pass

    def validar(self, registros: list[dict[str, Any]]) -> None:
        """Valida antes da carga (RF-64). Padrão: schema de fato_indicador; dimensões sobrescrevem."""
        validar_registros(registros)

    def _preservar_defasado(self) -> None:
        """Regrava o último valor válido com qualidade='defasado' (RF-66 — nunca grava zero)."""
        if self.tabela_destino == "fato_indicador":
            ultimo = self.carregador.obter_ultimo_valor_valido(self.id_indicador)
            anteriores = [ultimo] if ultimo else []
        else:
            anteriores = self.carregador.obter_validos_por_fonte(self.tabela_destino, self.id_fonte)
        defasados = [{**r, "qualidade": "defasado"} for r in anteriores]
        self.carregador.carregar_merge(
            defasados, tabela=self.tabela_destino, chave=self.chave_merge
        )

    def executar(self) -> dict[str, Any]:
        """
        Orquestra o ciclo de vida completo da coleta seguindo o Anexo D do PRD:
        Conformidade -> Extrair -> Hash -> Dedupe -> Salvar Raw -> Transformar -> Validar -> Carregar -> Log
        """
        inicio = time.time()
        id_execucao = str(uuid.uuid4())
        erro_msg: str | None = None

        # 1. Guarda de conformidade (robots.txt / termos) — RF-71
        # Não realiza nenhuma requisição de rede se estiver restrito
        checar_conformidade_coleta(self.metadata_fonte or {"ID": self.id_fonte})

        # 2. Extração com salvaguarda contra falha de rede (RF-66)
        try:
            bruto = self.extrair()
        except Exception as e:
            erro_msg = f"Falha de extração na fonte {self.id_fonte}: {e!s}"
            # Preserva o último valor válido com qualidade='defasado' (RF-66 - Nunca grava zero)
            self._preservar_defasado()

            duracao_ms = int((time.time() - inicio) * 1000)
            emitir_log(
                id_execucao=id_execucao,
                id_fonte=self.id_fonte,
                id_indicador=self.id_indicador,
                status="falha_extração",
                duracao_ms=duracao_ms,
                erro=erro_msg,
            )
            raise FonteIndisponivelError(erro_msg) from e

        # 3. Cálculo do Hash SHA-256 e Deduplicação (RF-62)
        h = calcular_hash_sha256(bruto)
        if self.armazenamento.hash_ja_processado(self.id_fonte, h):
            duracao_ms = int((time.time() - inicio) * 1000)
            log_res = emitir_log(
                id_execucao=id_execucao,
                id_fonte=self.id_fonte,
                id_indicador=self.id_indicador,
                status="sem_mudanca",
                bytes_processados=len(bruto),
                duracao_ms=duracao_ms,
                hash_origem=h,
            )
            return log_res

        # 4. Salvar arquivo bruto imutável na Zona Raw (RF-61)
        self.armazenamento.salvar_raw(self.id_fonte, bruto, h)

        # 5. Transformação
        registros = self.transformar(bruto)

        # 6. Validação dos registros (RF-64, RF-65)
        self.validar(registros)

        # Ajuste de flags e checagem 3-sigma por registro
        for r in registros:
            r["hash_origem"] = h
            if "qualidade" not in r:
                r["qualidade"] = "ok"

            # Checagem de variação 3-sigma se houver valor numérico
            if r.get("valor_num") is not None:
                val = float(r["valor_num"])
                st_sig = checar_variacao_3_sigma(val, [val])  # mock de série histórica
                if st_sig == "suspeito":
                    r["qualidade"] = "suspeito"

        # 7. Carga idempotente via MERGE (RF-67)
        linhas_carregadas = self.carregador.carregar_merge(
            registros, tabela=self.tabela_destino, chave=self.chave_merge
        )

        # Contagem de municípios cobertos
        mun_cobertos = len({r["id_municipio"] for r in registros if r.get("id_municipio")})
        duracao_ms = int((time.time() - inicio) * 1000)

        # 8. Log Estruturado (PRD §11.3)
        return emitir_log(
            id_execucao=id_execucao,
            id_fonte=self.id_fonte,
            id_indicador=self.id_indicador,
            status="ok",
            linhas_processadas=linhas_carregadas,
            municipios_cobertos=mun_cobertos,
            duracao_ms=duracao_ms,
            bytes_processados=len(bruto),
            hash_origem=h,
        )
