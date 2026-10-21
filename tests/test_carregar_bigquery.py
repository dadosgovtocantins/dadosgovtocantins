"""
scripts/carregar_bigquery.py e src/sql/aplicar_ddl.sh (Task 31, BigQuery Sandbox).
Sem nuvem: coletores com rede_gravada, cliente BigQuery simulado e um `bq` falso no PATH.
"""

import json
import os
import re
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from google.cloud import bigquery
from scripts import carregar_bigquery as cb
from src.coletor_base.http import ClienteHTTP
from src.coletores import siconfi

RAIZ = Path(__file__).parents[1]
CATALOGO = json.loads((RAIZ / "src" / "ui" / "data" / "painel_indicadores.json").read_text("utf-8"))


@pytest.fixture
def hoje_2026(monkeypatch):
    class Agora(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 14, tzinfo=UTC)

    monkeypatch.setattr(siconfi, "datetime", Agora)


def _schema(tabela: str) -> list[bigquery.SchemaField]:
    ddl = (cb.DDL / f"{tabela}.sql").read_text("utf-8")
    colunas = re.findall(r"^\s+(\w+)\s+([A-Z0-9]+)\s+(NOT NULL)?", ddl, re.M)
    return [
        bigquery.SchemaField(c, t, mode="REQUIRED" if nn else "NULLABLE") for c, t, nn in colunas
    ]


def _recusa_como_o_bigquery(linhas, schema):
    """As regras que já derrubaram cargas reais: NUMERIC com até 9 casas; REQUIRED sem nulo."""
    for r in linhas:
        for c in schema:
            v = r.get(c.name)
            if c.mode == "REQUIRED" and v is None:
                raise ValueError(f"400 campo obrigatório nulo: {c.name}")
            if c.field_type == "NUMERIC" and isinstance(v, float):
                casas = repr(v).split(".")[1] if "." in repr(v) else ""
                if "e" in casas or len(casas) > 9:
                    raise ValueError(f"400 Invalid NUMERIC value: {v!r} Field: {c.name}")


class ClienteFalso:
    project = "proj-teste"

    def __init__(self):
        self.cargas, self.renovadas, self.versao = {}, {}, {}

    def get_table(self, ref):
        nome = ref.rsplit(".", 1)[1]
        etag = self.versao.setdefault(ref, 0)
        return SimpleNamespace(ref=ref, nome=nome, schema=_schema(nome), expires=None, etag=etag)

    def load_table_from_json(self, linhas, tabela, job_config):
        _recusa_como_o_bigquery(linhas, job_config.schema)
        self.cargas[tabela.ref] = (linhas, job_config.write_disposition)
        self.versao[tabela.ref] += 1  # como no BigQuery: a carga muda o etag da tabela
        return SimpleNamespace(result=lambda: None)

    def update_table(self, tabela, campos):
        if tabela.etag != self.versao[tabela.ref]:  # o BigQuery devolve 412 Precondition Failed
            raise RuntimeError("412 Precondition check failed (etag de antes da carga)")
        self.renovadas[tabela.ref] = tabela.expires


@pytest.fixture
def coletas(rede_gravada, hoje_2026):
    return {f: cb.coletar(f) for f in cb.FONTES}


def test_monta_as_7_tabelas_com_os_dados_reais(coletas):
    t = cb.montar_tabelas(coletas, CATALOGO)
    assert len(t["dim_municipio"]) == 139 and len(t["dim_orgao"]) == 14
    assert (
        len(t["dim_titular"]) == 140 and len(t["dim_fonte"]) == 9 and len(t["dim_indicador"]) == 8
    )
    por_fonte = {f: sum(r["id_fonte"] == f for r in t["fato_indicador"]) for f in cb.IMPLEMENTADOS}
    assert por_fonte["TO-TER-01"] == 139 * 3 and all(por_fonte.values())
    assert all(len(r["hash_origem"]) == 64 for r in t["fato_indicador"] + t["dim_titular"])
    palmas = [
        r
        for r in t["fato_indicador"]
        if r["id_indicador"] == "pib_municipal" and r["id_municipio"] == "1721000"
    ]
    assert max(palmas, key=lambda r: r["periodo_ref"])["valor_num"] == 14_168_469.0
    # ausente nunca vira zero: Aguiarnópolis não publicou RCL e não tem linha
    assert not [
        r
        for r in t["fato_indicador"]
        if r["id_indicador"] == "receita_corrente_liquida" and r["id_municipio"] == "1700301"
    ]
    assert {d["data_ref"] for d in t["dim_tempo"]} == {
        r["periodo_ref"] for r in t["fato_indicador"]
    }


def test_carga_substitui_o_conteudo_e_renova_a_expiracao(coletas):
    cliente = ClienteFalso()
    n = cb.carregar(cliente, "dev", cb.montar_tabelas(coletas, CATALOGO))
    assert n["dim_municipio"] == 139 and n["dim_titular"] == 140
    assert set(cliente.cargas) == {f"proj-teste.dev_mart.{t}" for t in n}
    assert {modo for _, modo in cliente.cargas.values()} == {
        bigquery.WriteDisposition.WRITE_TRUNCATE
    }
    limite = datetime.now(UTC) + timedelta(days=60)
    assert all(e < limite for e in cliente.renovadas.values()) and len(cliente.renovadas) == 7
    # só as colunas da tabela vão na carga
    linhas, _ = cliente.cargas["proj-teste.dev_mart.fato_indicador"]
    campos = {c.name for c in _schema("fato_indicador")}
    assert set().union(*map(set, linhas)) <= campos


def test_numeric_com_lixo_de_ponto_flutuante_e_arredondado_a_9_casas():
    """Carga real de 20/10 recusada: 41355172.17 / 1000 = 41355.172170000005 (12 casas)."""
    cliente = ClienteFalso()
    linha = {
        "valor_num": 41_355_172.17 / 1000,
        "id_registro": "receita_corrente_liquida:TO:1700000:2025",
        "id_indicador": "receita_corrente_liquida",
        "periodo_ref": "2025-01-01",
        "periodicidade": "Anual",
        "id_fonte": "TO-REC-02",
        "esfera_fonte": "federal",
        "dt_coleta": "2026-10-20T00:00:00+00:00",
        "qualidade": "ok",
    }
    cb.carregar(cliente, "dev", {"fato_indicador": [linha]})
    (enviada,), _ = cliente.cargas["proj-teste.dev_mart.fato_indicador"]
    assert enviada["valor_num"] == 41355.17217


def test_fonte_com_erro_nao_carrega_a_tabela_dela(rede_gravada, hoje_2026, monkeypatch):
    ok = ClienteHTTP.get

    def get(self, url, headers=None):
        if "/agregados/6579/" in url:
            raise OSError("fora do ar")
        return ok(self, url, headers)

    monkeypatch.setattr(ClienteHTTP, "get", get)
    cliente = ClienteFalso()
    codigo = cb.main(["--ambiente", "dev"], cliente=cliente)
    assert codigo == 1
    assert "proj-teste.dev_mart.fato_indicador" not in cliente.cargas  # fica a carga anterior
    assert "proj-teste.dev_mart.dim_titular" in cliente.cargas  # TSE ok: carrega


def _aplicar_ddl(ambiente: str, env: dict | None = None) -> subprocess.CompletedProcess:
    comando = [
        "/bin/bash",
        str(RAIZ / "src" / "sql" / "aplicar_ddl.sh"),
        ambiente,
    ]  # fixo, sem entrada externa
    return subprocess.run(comando, env=env, capture_output=True, text=True, timeout=60)  # noqa: S603


def test_aplicar_ddl_sem_dml_sem_particao_e_com_teto(tmp_path):
    """Um `bq` falso no PATH grava o SQL recebido: nada de INSERT, nada de PARTITION, sempre com teto."""
    log = tmp_path / "bq.log"
    falso = tmp_path / "bq"
    falso.write_text(f'#!/usr/bin/env bash\nprintf "%s\\n=====\\n" "$*" >> "{log}"\n', "utf-8")
    falso.chmod(0o755)
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"}
    assert _aplicar_ddl("hml", env=env).returncode == 0
    chamadas = log.read_text("utf-8").split("=====\n")[:-1]
    assert len(chamadas) == 7
    for c in chamadas:
        assert (
            "--maximum_bytes_billed=100000000" in c and "CREATE TABLE IF NOT EXISTS `hml_mart." in c
        )
        assert "INSERT" not in c and "PARTITION BY" not in c and "ds_mart." not in c
    assert any('("ambiente", "hml")' in c for c in chamadas)  # rótulo do dim_titular ajustado


def test_aplicar_ddl_recusa_ambiente_invalido():
    r = _aplicar_ddl("prod")
    assert r.returncode == 2 and "ambiente inválido" in r.stderr
