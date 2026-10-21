"""
Testes das Telas de Apoio e Exportação CSV (Task 22).
"""

from pathlib import Path

import pytest


def test_index_antigo_contem_botoes_apoio():
    index_path = Path(__file__).parents[2] / "index-antigo.html"
    if not index_path.exists():
        pytest.skip("index-antigo.html é artefato local, fora do Git desde 21/10/2026")
    html = index_path.read_text("utf-8")

    assert 'id="btn-sobre"' in html
    assert 'id="btn-metodologia"' in html
    assert 'id="btn-export-csv"' in html
    assert 'id="modal-info"' in html


def test_app_js_contem_exportar_csv_e_modais():
    app_js_path = Path(__file__).parents[2] / "src" / "ui" / "app.js"
    assert app_js_path.exists()
    conteudo = app_js_path.read_text("utf-8")

    assert "exportarCSV" in conteudo
    assert "abrirModalSobre" in conteudo
    assert "abrirModalMetodologia" in conteudo
