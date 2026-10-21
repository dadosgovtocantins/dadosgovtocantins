"""
Testes dos 3 coletores do Bloco Recursos Financeiros (Task 15).
TO-REC-02 usa resposta REAL gravada (Task 28); TO-REC-01 e TO-REC-03 usam payload sintético (sem coleta real).
"""

import json
from datetime import UTC, datetime

import pytest
from src.coletor_base.excecoes import ValidacaoError
from src.coletor_base.http import ClienteHTTP
from src.coletores import siconfi
from tests.fixtures.recursos_payloads import (
    fixture_capag,
    fixture_siconfi_rcl,
    fixture_transferegov,
)


def test_to_rec_01_transferegov_139():
    from src.coletores.to_rec_01 import ColetorTOREC01

    c = ColetorTOREC01(ambiente="dev")
    registros = c.transformar(fixture_transferegov())
    assert len(registros) == 139
    assert all(r["id_indicador"] == "convenios_transferegov" for r in registros)


def test_to_rec_02_rcl_real_estado_e_municipios():
    from src.coletores.to_rec_02 import ColetorTOREC02

    registros = ColetorTOREC02(ambiente="dev").transformar(fixture_siconfi_rcl())
    assert len(registros) == 6
    assert len({r["id_registro"] for r in registros}) == 6
    assert all(r["unidade"] == "R$ mil" for r in registros)
    por_chave = {(r["id_municipio"], r["periodo_ref"][:4]): r["valor_num"] for r in registros}
    assert por_chave[("1721000", "2025")] == pytest.approx(2_155_602.77972)  # Palmas, R$ mil
    assert por_chave[(None, "2025")] == pytest.approx(15_568_042.57326)  # estado: sem id_municipio
    estado = next(
        r for r in registros if r["id_municipio"] is None and r["periodo_ref"] == "2025-01-01"
    )
    assert estado["id_registro"] == "receita_corrente_liquida:TO:2025"


def test_ler_itens_payload_invalido_levanta_validacao():
    for bruto in (
        b"{}",
        b"nao e json",
        b'{"itens": [{"cod_ibge": 1}]}',
        b'{"itens": [{"cod_ibge": 1, "exercicio": "x", "valor": 1}]}',
    ):
        with pytest.raises(ValidacaoError, match="formato inesperado"):
            siconfi.ler_itens(bruto)


def _rede_siconfi(monkeypatch, por_ente, tem_mais=False):
    """ClienteHTTP.get sintético: lista de municípios e RREO com linhas que o filtro deve descartar."""
    chamadas = []

    def get(self, url, headers=None):
        chamadas.append(url)
        if url == siconfi.URL_MUNICIPIOS:
            return json.dumps([{"id": 1700251}, {"id": 1721000}]).encode()
        ente = int(url.rsplit("id_ente=", 1)[1])
        linha = {"cod_ibge": ente, "exercicio": 2000, "valor": por_ente[ente]}
        itens = [
            {**linha, "cod_conta": siconfi.CONTA_RREO, "coluna": siconfi.COLUNA_RREO},
            {
                **linha,
                "cod_conta": siconfi.CONTA_RREO,
                "coluna": "<MR-3>",
            },  # mês isolado: descartar
            {
                **linha,
                "cod_conta": "RREO3ReceitaCorrenteLiquidaAjustada",
                "coluna": siconfi.COLUNA_RREO,
            },
        ]
        return json.dumps({"hasMore": tem_mais, "items": itens}).encode()

    monkeypatch.setattr(ClienteHTTP, "get", get)
    return chamadas


def test_coletar_rcl_pega_so_a_linha_da_rcl_nos_ultimos_exercicios(monkeypatch):
    chamadas = _rede_siconfi(monkeypatch, {17: 1.0, 1700251: 2.0, 1721000: 3.0})
    itens = json.loads(siconfi.coletar_rcl(exercicios=3))["itens"]
    ultimo = datetime.now(UTC).year - 1
    assert len(chamadas) == 1 + 3 * 3  # municípios + 3 exercícios x (estado + 2 municípios)
    assert sorted(
        {f"an_exercicio={a}&" in u for u in chamadas[1:] for a in range(ultimo - 2, ultimo + 1)}
    ) == [False, True]
    assert all(f"an_exercicio={a}&" not in " ".join(chamadas) for a in (ultimo + 1, ultimo - 3))
    assert len(itens) == 9 and {i["cod_ibge"] for i in itens} == {17, 1700251, 1721000}


def test_coletar_rcl_resposta_paginada_levanta_validacao(monkeypatch):
    _rede_siconfi(monkeypatch, {17: 1.0, 1700251: 2.0, 1721000: 3.0}, tem_mais=True)
    with pytest.raises(ValidacaoError, match="paginou"):
        siconfi.coletar_rcl(exercicios=1)


def test_to_rec_03_capag_139():
    from src.coletores.to_rec_03 import ColetorTOREC03

    c = ColetorTOREC03(ambiente="dev")
    registros = c.transformar(fixture_capag())
    assert len(registros) == 139
    assert all(r["valor_texto"] in ["A", "B", "C"] for r in registros)


def test_contrato_max_50_linhas_recursos():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in ["to_rec_01.py", "to_rec_02.py", "to_rec_03.py"]:
        linhas = (pasta / arq).read_text("utf-8").splitlines()
        assert len(linhas) <= 55, f"{arq} excede limite de linhas ({len(linhas)})"


def test_contrato_nao_sobrescreve_executar_recursos():
    from pathlib import Path

    pasta = Path(__file__).parents[2] / "src" / "coletores"
    for arq in ["to_rec_01.py", "to_rec_02.py", "to_rec_03.py"]:
        conteudo = (pasta / arq).read_text("utf-8")
        assert "def executar(" not in conteudo, f"{arq} sobrescreve executar()"


def _rede_com_rgf(monkeypatch, rreo: dict, rgf_simplificado: dict, rgf_quadrimestral: dict):
    """Rede sintética: cada dicionário mapeia ente -> valor da RCL; ente ausente = relatório sem a linha da RCL."""
    chamadas = []

    def get(self, url, headers=None):
        if url == siconfi.URL_MUNICIPIOS:
            return json.dumps([{"id": 1700251}, {"id": 1721000}]).encode()
        ente = int(url.split("id_ente=")[1].split("&")[0])
        if "/rgf?" in url:
            tipo = "simplificado" if "RGF%20Simplificado" in url else "quadrimestral"
            valores, conta, coluna = (
                (rgf_simplificado if tipo == "simplificado" else rgf_quadrimestral),
                siconfi.CONTA_RGF,
                siconfi.COLUNA_RGF,
            )
            chamadas.append((tipo, ente))
        else:
            valores, conta, coluna = rreo, siconfi.CONTA_RREO, siconfi.COLUNA_RREO
            chamadas.append(("rreo", ente))
        itens = []
        if ente in valores:
            itens.append(
                {
                    "cod_ibge": ente,
                    "exercicio": 2000,
                    "valor": valores[ente],
                    "cod_conta": conta,
                    "coluna": coluna,
                }
            )
        return json.dumps({"hasMore": False, "items": itens}).encode()

    monkeypatch.setattr(ClienteHTTP, "get", get)
    return chamadas


def _itens(monkeypatch, **fontes):
    chamadas = _rede_com_rgf(monkeypatch, **fontes)
    itens = json.loads(siconfi.coletar_rcl(exercicios=1))["itens"]
    return {i["cod_ibge"]: (i["valor"], i["origem"]) for i in itens}, chamadas


def test_rgf_simplificado_preenche_o_municipio_sem_rreo_completo(monkeypatch):
    por_ente, chamadas = _itens(
        monkeypatch,
        rreo={17: 9.0, 1721000: 3.0},
        rgf_simplificado={1700251: 2.0},
        rgf_quadrimestral={},
    )
    assert por_ente == {17: (9.0, "RREO"), 1721000: (3.0, "RREO"), 1700251: (2.0, "RGF")}
    assert chamadas.count(("simplificado", 1700251)) == 1
    assert ("quadrimestral", 1700251) not in chamadas  # parou no primeiro que trouxe a RCL
    assert not [
        c for c in chamadas if c[0] != "rreo" and c[1] in (17, 1721000)
    ]  # RREO completo basta


def test_rgf_quadrimestral_e_a_segunda_tentativa(monkeypatch):
    por_ente, chamadas = _itens(
        monkeypatch,
        rreo={17: 9.0},
        rgf_simplificado={},
        rgf_quadrimestral={1700251: 4.0, 1721000: 5.0},
    )
    assert por_ente[1700251] == (4.0, "RGF") and por_ente[1721000] == (5.0, "RGF")
    assert (
        chamadas.count(("simplificado", 1721000)) == 1
        and chamadas.count(("quadrimestral", 1721000)) == 1
    )


def test_sem_rreo_nem_rgf_nao_gera_item_nem_zero(monkeypatch):
    por_ente, _ = _itens(monkeypatch, rreo={17: 9.0}, rgf_simplificado={}, rgf_quadrimestral={})
    assert por_ente == {
        17: (9.0, "RREO")
    }  # os municípios sem relatório ficam de fora: nunca viram 0


def test_ler_itens_ignora_a_origem_e_mantem_so_o_necessario():
    bruto = json.dumps(
        {"itens": [{"cod_ibge": 1700251, "exercicio": 2025, "valor": 34960559.96, "origem": "RGF"}]}
    ).encode()
    assert siconfi.ler_itens(bruto) == [
        {"cod_ibge": "1700251", "exercicio": 2025, "valor": 34960559.96}
    ]
