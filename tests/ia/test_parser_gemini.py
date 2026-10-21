"""
Testes unitários do módulo de parsing com Gemini IA (Task 21).
"""

import json

from src.ia.parser_gemini import extrair_indicadores_documento


def test_extrair_indicadores_marca_gerado_por_ia():
    mock_json = json.dumps(
        [
            {
                "id_indicador": "orcamento_anual_pdf",
                "id_municipio": "1721000",
                "periodo_ref": "2023-01-01",
                "valor_num": 450000.0,
                "unidade": "BRL",
            }
        ]
    )

    res = extrair_indicadores_documento(
        texto_documento="Relatório Anual PDF SEFAZ 2023",
        id_fonte="TO-PDF-01",
        id_orgao="SEFAZ-TO",
        mock_response=mock_json,
    )

    assert len(res) == 1
    reg = res[0]
    assert reg["gerado_por_ia"] is True
    assert reg["id_orgao"] == "SEFAZ-TO"
    assert reg["valor_num"] == 450000.0


def test_extrair_documento_vazio_retorna_lista_vazia():
    res = extrair_indicadores_documento("", "TO-PDF-01", "SEFAZ-TO")
    assert len(res) == 0
