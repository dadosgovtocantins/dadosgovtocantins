"""
scripts/automacao_coleta.py nunca grava dado simulado quando a API falha (Task 28, RF-55).
Rodam sem rede: requests.get é substituído por respostas gravadas ou por uma falha.
"""

import csv
import importlib.util
from pathlib import Path

import pytest
from tests.fixtures.ibge_payloads import fixture_populacao

RAIZ = Path(__file__).parents[1]


def _carregar_script():
    spec = importlib.util.spec_from_file_location(
        "automacao_coleta", RAIZ / "scripts" / "automacao_coleta.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class _Resposta:
    def __init__(self, corpo):
        self._corpo = corpo

    def raise_for_status(self):
        pass

    def json(self):
        return self._corpo


def test_falha_da_api_nao_grava_dado_simulado(monkeypatch, tmp_path):
    mod = _carregar_script()
    monkeypatch.setattr(mod, "DATA_DIR", str(tmp_path))

    def falha(*args, **kwargs):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(mod.requests, "get", falha)
    assert mod.coletar_dados_ibge_to() is None
    assert mod.coletar_dados_siconfi_to() is None
    with pytest.raises(SystemExit) as saida:
        mod.executar_pipeline_completo()
    assert saida.value.code == 1
    assert list(tmp_path.iterdir()) == []  # nenhum CSV foi sobrescrito


def test_resposta_real_gera_csv_com_139_municipios(monkeypatch, tmp_path):
    import json

    mod = _carregar_script()
    monkeypatch.setattr(mod, "DATA_DIR", str(tmp_path))
    itens_siconfi = {"items": [{"an_exercicio": 2023, "cod_conta": "X", "valor": 1.0}]}

    def get(url, **kwargs):
        if "servicodados.ibge.gov.br" in url:
            return _Resposta(json.loads(fixture_populacao()))
        return _Resposta(itens_siconfi)

    monkeypatch.setattr(mod.requests, "get", get)
    mod.executar_pipeline_completo()
    with open(tmp_path / "ibge_populacao_to.csv", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 139
    palmas = next(r for r in linhas if r["id_municipio"] == "1721000")
    assert palmas["populacao_estimada"] == "323625"
    assert (tmp_path / "siconfi_execucao_to.csv").exists()
