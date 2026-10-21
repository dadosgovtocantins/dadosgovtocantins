"""
Testes unitários e de integração do framework ColetorBase (Task 06).
"""

from typing import Any, ClassVar
from unittest.mock import MagicMock

import pytest
from src.coletor_base.armazenamento import GerenciadorArmazenamentoRaw
from src.coletor_base.base import ColetorBase
from src.coletor_base.conformidade import checar_conformidade_coleta
from src.coletor_base.excecoes import ColetaBloqueadaError, FonteIndisponivelError, ValidacaoError
from src.coletor_base.http import ClienteHTTP
from src.coletor_base.validacao import checar_variacao_3_sigma, validar_registros
from src.coletores.to_ter_01 import ColetorTOTER01


class ColetorMock(ColetorBase):
    id_fonte = "TO-TEST-01"
    id_indicador = "teste_indicador"
    metadata_fonte: ClassVar[dict[str, Any]] = {
        "ID": "TO-TEST-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo",
    }

    def __init__(self, payload_bytes: bytes = b'{"dado": 1}', tmp_path=None):
        super().__init__(ambiente="dev")
        self.payload = payload_bytes
        self.should_fail = False
        if tmp_path:
            self.armazenamento = GerenciadorArmazenamentoRaw(diretorio_local=tmp_path)

    def extrair(self) -> bytes:
        if self.should_fail:
            raise ConnectionError("Rede indisponível")
        return self.payload

    def transformar(self, bruto: bytes) -> list[dict]:
        return [
            {
                "id_registro": "teste:1700001:2024",
                "id_indicador": self.id_indicador,
                "id_fonte": self.id_fonte,
                "id_municipio": "1700001",
                "periodo_ref": "2024-01-01",
                "valor_num": 100.0,
                "valor_texto": None,
                "qualidade": "ok",
            }
        ]


def test_conformidade_coleta_bloqueada():
    meta_bloqueada = {
        "ID": "TO-BLOQ-01",
        "RESTRIÇÃO ROBOTS/TERMOS": "Sim - Acesso proibido por robots.txt",
    }
    with pytest.raises(ColetaBloqueadaError, match="Coleta interrompida por design"):
        checar_conformidade_coleta(meta_bloqueada)


def test_execucao_coletor_sucesso_e_deduplicacao(tmp_path):
    coletor = ColetorMock(payload_bytes=b'{"valor": 123}', tmp_path=tmp_path)
    res1 = coletor.executar()
    assert res1["status"] == "ok"
    assert res1["linhas_processadas"] == 1

    # Segunda execução com payload idêntico deve retornar sem_mudanca (RF-62)
    res2 = coletor.executar()
    assert res2["status"] == "sem_mudanca"


def test_validacao_registros_nulo_e_periodo():
    with pytest.raises(ValidacaoError, match="periodo_ref"):
        validar_registros([{"id_indicador": "x", "id_fonte": "f", "valor_num": 10}])

    with pytest.raises(ValidacaoError, match="não podem ser ambos nulos"):
        validar_registros(
            [
                {
                    "id_indicador": "x",
                    "id_fonte": "f",
                    "periodo_ref": "2024-01-01",
                    "valor_num": None,
                    "valor_texto": None,
                }
            ]
        )


def test_checar_variacao_3_sigma():
    historico = [100.0, 102.0, 99.0, 101.0, 100.0]
    assert checar_variacao_3_sigma(101.0, historico) == "ok"
    assert checar_variacao_3_sigma(200.0, historico) == "suspeito"


def test_falha_de_extracao_preserva_defasado(tmp_path):
    coletor = ColetorMock(payload_bytes=b'{"valor": 456}', tmp_path=tmp_path)
    coletor.executar()  # Primeira execução salva ok

    # Segunda execução falha
    coletor.should_fail = True
    coletor.armazenamento.hash_ja_processado = MagicMock(return_value=False)
    with pytest.raises(FonteIndisponivelError):
        coletor.executar()


def test_coletor_referencia_to_ter_01(tmp_path, rede_gravada):
    coletor = ColetorTOTER01(ambiente="dev")
    coletor.armazenamento = GerenciadorArmazenamentoRaw(diretorio_local=tmp_path)
    res = coletor.executar()
    assert res["status"] == "ok"
    assert res["linhas_processadas"] == 139 * 3  # 139 municípios x 3 anos de estimativa
    assert res["municipios_cobertos"] == 139


def test_coletor_referencia_linhas_codigo():
    import pathlib

    caminho = pathlib.Path(__file__).parents[2] / "src" / "coletores" / "to_ter_01.py"
    linhas = caminho.read_text(encoding="utf-8").strip().splitlines()
    # RNF-E02: Coletor de referência em <= 50 linhas
    assert len(linhas) <= 50, f"Coletor excedeu 50 linhas: {len(linhas)}"


def test_cliente_http():
    cliente = ClienteHTTP(delay_segundos=0.0)
    assert "PainelTOEmDados" in cliente.user_agent
