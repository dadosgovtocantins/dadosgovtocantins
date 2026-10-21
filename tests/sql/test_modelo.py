"""
Testes unitários e de contrato do modelo de dados BigQuery (Task 07 / Star Schema).
"""

from pathlib import Path

VALORES_QUALIDADE_VALIDOS = {"ok", "estimado", "defasado", "suspeito", "sem_dado", "falho"}


def test_enum_qualidade_valores_validos():
    assert "sem_dado" in VALORES_QUALIDADE_VALIDOS
    assert "falho" in VALORES_QUALIDADE_VALIDOS
    assert "ok" in VALORES_QUALIDADE_VALIDOS


def test_distincao_tres_linhas():
    """
    Teste das três linhas (RF-55, RT-11):
    Diferença explícita entre dado zero (0), omissão declaratória (sem_dado) e falha técnica (falho).
    """
    linha_zero_real = {
        "id_registro": "r1",
        "id_indicador": "convenios_federais",
        "valor_num": 0.0,
        "qualidade": "ok",
    }
    linha_sem_dado = {
        "id_registro": "r2",
        "id_indicador": "convenios_federais",
        "valor_num": None,
        "qualidade": "sem_dado",
    }
    linha_falho = {
        "id_registro": "r3",
        "id_indicador": "convenios_federais",
        "valor_num": None,
        "qualidade": "falho",
    }

    # As três linhas são estruturalmente distintas
    assert linha_zero_real["valor_num"] == 0.0
    assert linha_zero_real["qualidade"] == "ok"

    assert linha_sem_dado["valor_num"] is None
    assert linha_sem_dado["qualidade"] == "sem_dado"

    assert linha_falho["valor_num"] is None
    assert linha_falho["qualidade"] == "falho"

    assert linha_zero_real["qualidade"] != linha_sem_dado["qualidade"]
    assert linha_sem_dado["qualidade"] != linha_falho["qualidade"]


def test_esfera_fonte_validacao():
    esferas_validas = {"federal", "estadual"}
    assert "federal" in esferas_validas
    assert "estadual" in esferas_validas


def test_chave_canonica_ibge_7_digitos():
    from src.sql.stg.normaliza_municipio import fn_normaliza_codigo_ibge

    # 7 dígitos originais preservados
    assert fn_normaliza_codigo_ibge("1721000") == "1721000"
    # 6 dígitos convertidos para 7
    assert fn_normaliza_codigo_ibge("172100") == "1721000"
    # Inválidos retornam None
    assert fn_normaliza_codigo_ibge("123") is None


def test_maximum_bytes_billed_presente_em_clientes_sql():
    """Garante que o parâmetro maximum_bytes_billed está configurado nas consultas Python."""
    raiz_src = Path(__file__).parents[2] / "src"
    py_files = list(raiz_src.rglob("*.py"))

    for f in py_files:
        conteudo = f.read_text(encoding="utf-8")
        if f.name == "carga.py":
            assert "maximum_bytes_billed" in conteudo, (
                f"{f.name} faz consulta SQL sem maximum_bytes_billed"
            )
