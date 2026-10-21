"""
Testes das views da camada semântica e ranking municipal (Task 11).
"""

from pathlib import Path


def test_views_sql_existem():
    pasta_mart = Path(__file__).parents[2] / "src" / "sql" / "mart"
    for view in ["vw_tela_municipio.sql", "vw_tela_estado.sql", "vw_ranking_municipios.sql"]:
        arq = pasta_mart / view
        assert arq.exists(), f"View SQL {view} não encontrada"
        conteudo = arq.read_text("utf-8")
        assert "CREATE OR REPLACE VIEW" in conteudo, f"{view} deve conter CREATE OR REPLACE VIEW"


def test_vw_ranking_usa_dense_rank():
    pasta_mart = Path(__file__).parents[2] / "src" / "sql" / "mart"
    conteudo = (pasta_mart / "vw_ranking_municipios.sql").read_text("utf-8")
    assert "DENSE_RANK()" in conteudo
    assert "SAFE_DIVIDE" in conteudo
    assert "LAG(" in conteudo
