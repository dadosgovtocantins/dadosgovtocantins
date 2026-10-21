"""
Testes de unidade para a leitura e validação do Catálogo em dois níveis (Task 04 / RF-80 a RF-84).
"""

import pytest
from src.catalogo.leitor import (
    CatalogoValidationError,
    validar_catalogo_fontes,
    validar_catalogo_indicadores,
)


@pytest.fixture
def fonte_valida():
    return {
        "ID": "TO-TER-01",
        "ÓRGÃO": "IBGE",
        "INDICADOR": "Estimativas de População",
        "ÁREA": "Território",
        "SISTEMA": "SIDRA",
        "O QUE REPRESENTA": "População",
        "LINK PÚBLICO": "http://example.com",
        "URL DA API": "http://api.example.com",
        "ENDPOINT": "/pop",
        "AUTENTICAÇÃO": "Nenhuma",
        "FORMATO": "JSON",
        "CLASSE DE FORMATO": "A",
        "PERIODICIDADE EXATA": "Anual",
        "DEFASAGEM": "1 ano",
        "ÚLTIMA ATUALIZAÇÃO": "2026-01-01",
        "HISTÓRICO DISPONÍVEL": "2010-2024",
        "NÍVEL GEOGRÁFICO": "Municipal",
        "GRANULARIDADE TEMPORAL": "Anual",
        "UNIDADE DE MEDIDA": "hab",
        "RESPONSÁVEL PELO DADO": "IBGE",
        "FONTE PRIMÁRIA/SECUNDÁRIA": "Primária",
        "TIPO DE FONTE": "Federal",
        "FONTE ABERTA EQUIVALENTE": "N/A",
        "PAINEL LAB63 RELACIONADO": "N/A",
        "POWER BI DATASET ID": "N/A",
        "POWER BI REPORT ID": "N/A",
        "ACESSO PÚBLICO SEM CADASTRO?": "Sim",
        "REUTILIZÁVEL?": "Sim",
        "API PÚBLICA?": "Sim",
        "DADOS REALMENTE ABERTOS?": "Sim",
        "QUADRANTE": "Q1",
        "ESCOPO": "In",
        "LICENÇA DE USO": "Domínio Público",
        "RESTRIÇÃO ROBOTS/TERMOS": "Não restritivo (31/08/2026)",
        "MÉTODO DE COLETA": "API",
        "STATUS DE VALIDAÇÃO": "Homologado",
        "NÍVEL DE CONFIABILIDADE": "DESATIVADA-MVP",
        "CLASSIFICAÇÃO": "A",
        "PRIORIDADE": "1",
        "OBSERVAÇÕES TÉCNICAS": "Nenhuma",
    }


@pytest.fixture
def indicador_valido():
    return {
        "id_indicador": "populacao_residente",
        "id_fonte": "TO-TER-01",
        "nome_exibicao": "População Residente",
        "definicao_cidadao": "Total de habitantes",
        "unidade": "hab",
        "sentido": "maior_melhor",
        "tela": "municipio",
        "ordem_card": "1",
        "icone": "users",
        "calculado": "FALSE",
        "formula": "",
        "status": "ativo",
    }


def test_validar_catalogo_fontes_sucesso(fonte_valida):
    mapa = validar_catalogo_fontes([fonte_valida])
    assert "TO-TER-01" in mapa
    assert mapa["TO-TER-01"].orgao == "IBGE"
    assert mapa["TO-TER-01"].classificacao == "A"


def test_validar_catalogo_fontes_id_duplicado(fonte_valida):
    with pytest.raises(CatalogoValidationError, match="ID duplicado"):
        validar_catalogo_fontes([fonte_valida, fonte_valida])


def test_validar_catalogo_fontes_robots_vazio(fonte_valida):
    fonte_valida["RESTRIÇÃO ROBOTS/TERMOS"] = ""
    with pytest.raises(CatalogoValidationError, match="RESTRIÇÃO ROBOTS/TERMOS"):
        validar_catalogo_fontes([fonte_valida])


def test_validar_catalogo_indicadores_sucesso(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    indicadores = validar_catalogo_indicadores([indicador_valido], mapa_fontes)
    assert len(indicadores) == 1
    assert indicadores[0].id_indicador == "populacao_residente"
    assert indicadores[0].id_fonte == "TO-TER-01"


def test_validar_catalogo_indicadores_fk_invalida(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    indicador_valido["id_fonte"] = "TO-INEXISTENTE"
    with pytest.raises(CatalogoValidationError, match="FK id_fonte 'TO-INEXISTENTE' não existe"):
        validar_catalogo_indicadores([indicador_valido], mapa_fontes)


def test_validar_catalogo_indicadores_unidade_multipla(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    indicador_valido["unidade"] = "hab, R$"
    with pytest.raises(CatalogoValidationError, match="apenas uma unidade"):
        validar_catalogo_indicadores([indicador_valido], mapa_fontes)


def test_validar_catalogo_indicadores_sentido_invalido(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    indicador_valido["sentido"] = "super_bom"
    with pytest.raises(CatalogoValidationError, match="'sentido' inválido"):
        validar_catalogo_indicadores([indicador_valido], mapa_fontes)


def test_validar_catalogo_indicadores_calculado_sem_formula(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    indicador_valido["calculado"] = "TRUE"
    indicador_valido["formula"] = ""
    with pytest.raises(CatalogoValidationError, match="exige preenchimento da coluna 'formula'"):
        validar_catalogo_indicadores([indicador_valido], mapa_fontes)


def test_validar_cobertura_fonte_classe_a_sem_indicador(fonte_valida, indicador_valido):
    mapa_fontes = validar_catalogo_fontes([fonte_valida])
    # Passa indicador para outra fonte existente para acionar a validação de cobertura de fonte_valida
    outra_fonte = dict(fonte_valida)
    outra_fonte["ID"] = "TO-SAU-01"
    outra_fonte["CLASSIFICAÇÃO"] = "D"
    mapa_fontes = validar_catalogo_fontes([fonte_valida, outra_fonte])
    indicador_valido["id_fonte"] = "TO-SAU-01"
    with pytest.raises(CatalogoValidationError, match="não possui nenhum indicador associado"):
        validar_catalogo_indicadores([indicador_valido], mapa_fontes)
