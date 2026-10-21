"""
Testes de integridade da Tela Município (Task 13 — Demo 2).
"""

import hashlib
import json
from pathlib import Path

import pytest


def test_index_antigo_estrutura_semantica():
    index_path = Path(__file__).parents[2] / "index-antigo.html"
    if not index_path.exists():
        pytest.skip("index-antigo.html é artefato local, fora do Git desde 21/10/2026")
    html = index_path.read_text("utf-8")

    assert "<title>Painel TO em Dados" in html
    assert 'id="aviso-nao-oficialidade"' in html
    assert 'id="select-municipio"' in html
    assert 'id="cards-grid"' in html
    assert "Unitins" in html


def test_municipios_to_json_contem_139():
    json_path = Path(__file__).parents[2] / "src" / "ui" / "data" / "municipios_to.json"
    assert json_path.exists()
    dados = json.loads(json_path.read_text("utf-8"))

    assert len(dados) == 139
    assert all(m["id_municipio"].startswith("17") for m in dados)
    assert all(len(m["id_municipio"]) == 7 for m in dados)


def test_app_js_importa_card_component():
    app_js_path = Path(__file__).parents[2] / "src" / "ui" / "app.js"
    assert app_js_path.exists()
    conteudo = app_js_path.read_text("utf-8")
    assert "renderKPICard" in conteudo
    assert "selecionarMunicipio" in conteudo


def test_raiz_serve_painel_novo():
    """A raiz abre o painel novo (Design Component)."""
    raiz = Path(__file__).parents[2]
    html = (raiz / "index.html").read_text("utf-8")
    assert "<x-dc>" in html
    assert "./support.js" in html
    assert "./src/ui/painel-logica.js" in html  # lógica pura carregada antes do runtime
    assert "data-dc-script" in html
    assert (raiz / "src" / "ui" / "painel-logica.js").exists()
    assert "sem vínculo com o Governo do Estado do Tocantins" in html


def test_arquivos_do_painel_tem_versao_pelo_conteudo():
    """Sem Cache-Control, o navegador pode reusar o .js/.css antigo com o index.html novo
    ("PainelLogica.titular is not a function", task 32). O ?v= é o início do SHA-256 do arquivo:
    mudou o arquivo, muda o endereço e o navegador busca de novo."""
    raiz = Path(__file__).parents[2]
    html = (raiz / "index.html").read_text("utf-8")
    for rel in ("src/ui/painel-logica.js", "src/ui/css/painel.css"):
        v = hashlib.sha256((raiz / rel).read_bytes()).hexdigest()[:8]
        assert f'"./{rel}?v={v}"' in html, f"atualize no index.html: ./{rel}?v={v}"
