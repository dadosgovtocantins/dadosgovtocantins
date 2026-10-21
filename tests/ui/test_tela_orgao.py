"""
Testes de integridade da Tela Órgão (Task 20 — Demo 4).
"""

from pathlib import Path

import pytest


def test_index_antigo_contem_aba_orgao():
    index_path = Path(__file__).parents[2] / "index-antigo.html"
    if not index_path.exists():
        pytest.skip("index-antigo.html é artefato local, fora do Git desde 21/10/2026")
    html = index_path.read_text("utf-8")

    assert 'id="tab-orgao"' in html
    assert "Visão por Órgão" in html


def test_app_js_contem_renderizacao_orgao():
    app_js_path = Path(__file__).parents[2] / "src" / "ui" / "app.js"
    assert app_js_path.exists()
    conteudo = app_js_path.read_text("utf-8")

    assert "renderizarTelaOrgao" in conteudo
    assert "maturidade-card" in conteudo
    assert "Índice de Maturidade" in conteudo
