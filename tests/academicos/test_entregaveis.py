"""
Testes de integridade dos Entregáveis Acadêmicos (Task 25).
"""

from pathlib import Path


def test_relatorio_pibiex_md_existe_e_completo():
    rel_path = Path(__file__).parents[2] / "docs" / "relatorio_pibiex.md"
    assert rel_path.exists()
    conteudo = rel_path.read_text("utf-8")

    assert "Unitins" in conteudo
    assert "PIBIEX" in conteudo
    assert "139 municípios" in conteudo
    assert "18 fontes" in conteudo


def test_artigo_maturidade_dados_md_existe():
    art_path = Path(__file__).parents[2] / "docs" / "artigo_maturidade_dados.md"
    assert art_path.exists()
    conteudo = art_path.read_text("utf-8")

    assert "Diagnóstico da Maturidade" in conteudo
    assert "Vaadin 8.9.2" in conteudo
    assert "Resumo" in conteudo
