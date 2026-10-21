"""
Testes de FinOps e Saúde da Operação (Task 23).
"""

from src.operacao.finops import auditoria_custo_zero, verificar_saude_operacao


def test_auditoria_custo_zero_dentro_do_limite():
    res = auditoria_custo_zero(500_000_000)  # 500 MB
    assert res["aprovado"] is True
    assert res["custo_estimado_brl"] == 0.0


def test_auditoria_custo_zero_excede_limite():
    res = auditoria_custo_zero(2_000_000_000)  # 2 GB
    assert res["aprovado"] is False


def test_verificar_saude_operacao_100_pct():
    fontes = [{"id": f"F{i}", "status": "ok"} for i in range(18)]
    res = verificar_saude_operacao(fontes)
    assert res["total_fontes_monitoradas"] == 18
    assert res["fontes_saudaveis"] == 18
    assert res["taxa_saude_pct"] == 100.0
