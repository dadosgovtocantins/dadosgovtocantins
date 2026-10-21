"""
Testes de integridade da Tela Estado (Task 17 — Demo 3).
"""

from pathlib import Path

import pytest


def test_index_antigo_contem_abas_navegacao():
    index_path = Path(__file__).parents[2] / "index-antigo.html"
    if not index_path.exists():
        pytest.skip("index-antigo.html é artefato local, fora do Git desde 21/10/2026")
    html = index_path.read_text("utf-8")

    assert 'id="tab-municipio"' in html
    assert 'id="tab-estado"' in html
    assert "Visão Geral do Estado (Tocantins)" in html


def test_app_js_contem_renderizacao_estado():
    app_js_path = Path(__file__).parents[2] / "src" / "ui" / "app.js"
    assert app_js_path.exists()
    conteudo = app_js_path.read_text("utf-8")

    assert "renderizarCardsEstado" in conteudo
    assert "pib_estadual" in conteudo
    assert "taxa_desocupacao_pnadc" in conteudo
    assert "alternarAba" in conteudo
