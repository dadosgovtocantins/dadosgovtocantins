"""
Testes automatizados de qualidade e validação do Gate 2 (Task 24).
"""

from pathlib import Path


def test_verificacao_golive_md_existe_e_aprovado():
    doc_path = Path(__file__).parents[2] / "docs" / "verificacao_golive.md"
    assert doc_path.exists()
    conteudo = doc_path.read_text("utf-8")

    assert "APROVADO PARA PUBLICAÇÃO" in conteudo
    assert "18 fontes ativas" in conteudo
    assert "Palmas" in conteudo
    assert "Araguaína" in conteudo


def test_cobertura_total_coletores_registrados():
    from src.cli import REGISTRO_COLETORES

    # 18 fontes do go-live (Task 24) + TO-GER-01 e TO-GER-02 (Task 30, titulares eleitos).
    esperado = 20
    assert len(REGISTRO_COLETORES) == esperado, (
        f"Esperado {esperado} fontes registradas, encontrado {len(REGISTRO_COLETORES)}"
    )
