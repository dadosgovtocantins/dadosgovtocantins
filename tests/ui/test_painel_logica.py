"""
Lógica pura do painel (src/ui/painel-logica.js), executada no Node (Task 29, correções da Task 26).
Cobre: variação sem ∞/NaN, ausente nunca vira zero (RF-55), "Não coletado" x "Sem dado", escala de moeda e telas de 8.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

MODULO = Path(__file__).parents[2] / "src" / "ui" / "painel-logica.js"

SCRIPT = """
const L = require(process.argv[1]);
const ind = { titulo: "t", fonte: "f", sentido: "maior_melhor" };
const dado = (s, i = ind) => L.dadoDe(i, s);
const desocup = { ...ind, varUni: "p.p.", sentido: "menor_melhor" };
const bloco = (nome, n) => ({ id: nome, nome, itens: [...Array(n).keys()].map((k) => ({ titulo: nome + k })) });
const telas = (tam) => L.montarTelas(tam.map((n, i) => bloco("B" + i, n)), 8);
const resumo = (ts) => ts.map((t) => t.blocos.map((b) => b.nome + ":" + b.itens.length));
const quadrado = [[[-48, -10], [-47, -10], [-47, -9], [-48, -9], [-48, -10]]];
console.log(JSON.stringify({
  moeda: [14168469, 141900, 800, -2e6].map((v) => L.escalaMoeda(v).unidade),
  varAnteriorZero: L.variacao(ind, dado([["2022", 0], ["2023", 5]])),
  varPontos: L.variacao(desocup, dado([["1T", 5.6], ["2T", 4.1]], desocup)),
  varPercentual: L.variacao(ind, dado([["2021", 100], ["2023", 110]])),
  varEstavel: L.variacao(ind, dado([["2022", 100], ["2023", 100.01]])),
  pontosInvalidos: dado([["2021", null], ["2022", "x"], ["2023", 7]]),
  semPontoValido: dado([["2021", null], ["2022", NaN]]),
  naoColetado: L.cartao(ind, null),
  carregando: L.cartao(ind, undefined),
  semDado: L.cartao(ind, []),
  moedaGrande: L.cartao({ ...ind, moeda: true }, [["2022", 11951579], ["2023", 14168469]]),
  moedaMil: L.cartao({ ...ind, moeda: true }, [["2023", 800]]),
  sparkBuraco: L.spark([1, null, 3]),
  sparkCurta: L.spark([5, null]),
  aviso: [L.aviso([{ itens: [{ temDado: true }, { temDado: false }] }], ""), L.aviso([{ itens: [{ temDado: false }] }], ""), L.aviso([], "Falhou")],
  continuacao: resumo(telas([3, 10])),
  estado20: resumo(telas([2, 2, 4, 3, 2, 7])),
  municipio14: resumo(telas([4, 2, 3, 3, 2])),
  titulares: [
    { nome: "EDUARDO SIQUEIRA CAMPOS", ano_eleicao: 2024 },
    { nome: "MARIA DO SOCORRO ", ano_eleicao: 2024 },
    { nome: "ISMAEL  BRITO", ano_eleicao: 2024 },
    { nome: "DA SILVA E JOÃO-PAULO DOS ANJOS", ano_eleicao: 2022 },
    { nome: "ZÉ", ano_eleicao: "2024" },
  ].map(L.titular),
  titularInvalido: [null, undefined, "x", {}, { nome: "" }, { nome: "   " }, { nome: 5 }, { nome: "A".repeat(81) }].map(L.titular),
  projecao: L.projetar({ features: [
    { geometry: { type: "Polygon", coordinates: quadrado }, properties: { cod_ibge: "1721000" } },
    { geometry: { type: "Polygon", coordinates: quadrado }, properties: { cod_ibge: "9999999" } },
    { geometry: null, properties: { cod_ibge: "1721000" } },
  ] }, { 1721000: ["Palmas", 1] }),
}));
"""


@pytest.fixture(scope="module")
def r():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node não instalado")
    comando = [node, "-e", SCRIPT, str(MODULO)]  # comando fixo, sem entrada externa
    saida = subprocess.run(comando, capture_output=True, text=True, check=True, timeout=30)  # noqa: S603
    return json.loads(saida.stdout)


def test_escala_da_moeda_pelo_tamanho(r):
    assert r["moeda"] == ["R$ bi", "R$ mi", "R$ mil", "R$ bi"]


def test_variacao_nunca_mostra_infinito_nem_nan(r):
    assert r["varAnteriorZero"] is None  # divisão por zero: sem variação, não "+∞%"
    assert r["varPercentual"]["varFmt"] == "+10,0%" and r["varPercentual"]["vs"] == "vs. 2021"
    assert r["varEstavel"]["varFmt"] == "estável" and r["varEstavel"]["seta"] == "ph-minus"


def test_variacao_em_pontos_respeita_o_sentido_do_indicador(r):
    """Desocupação (menor é melhor) caiu 1,5 p.p.: variação favorável."""
    assert r["varPontos"]["varFmt"] == "\u22121,5 p.p." and r["varPontos"]["aval"] == "bom"
    assert r["varPontos"]["seta"] == "ph-arrow-down-right"


def test_ausente_nunca_vira_zero(r):
    assert r["pontosInvalidos"]["v"] == 7 and r["pontosInvalidos"]["ant"] is None
    assert r["semPontoValido"] is None
    assert (
        r["sparkBuraco"]["pts"].count(" ") == 1 and "NaN" not in r["sparkBuraco"]["pts"]
    )  # 2 pontos válidos
    assert r["sparkCurta"] == {}


def test_nao_coletado_x_sem_dado_x_carregando(r):
    assert r["naoColetado"]["valorFmt"] == "Não coletado" and r["naoColetado"]["temDado"] is False
    assert r["semDado"]["valorFmt"] == "Sem dado" and r["semDado"]["temDado"] is False
    assert r["carregando"]["valorFmt"] == "Carregando"


def test_cartao_de_moeda_escolhe_a_unidade(r):
    g, m = r["moedaGrande"], r["moedaMil"]
    assert (g["valorFmt"], g["unidade"], g["varFmt"], g["fonteFmt"]) == (
        "14,2",
        "R$ bi",
        "+18,5%",
        "f, 2023",
    )
    assert (m["valorFmt"], m["unidade"], m["temVar"]) == ("800", "R$ mil", False)


def test_aviso_conta_indicadores_reais(r):
    assert r["aviso"] == [
        "1 de 2 indicadores com dados reais",
        "Nenhum indicador coletado nesta visão",
        "Falhou",
    ]


def test_telas_de_ate_8_cartoes_sem_perder_nenhum(r):
    for chave, total in (("estado20", 20), ("municipio14", 14), ("continuacao", 13)):
        contagem = [sum(int(b.split(":")[1]) for b in tela) for tela in r[chave]]
        assert all(c <= 8 for c in contagem), (chave, r[chave])
        assert sum(contagem) == total
    assert len(r["estado20"]) == 3  # o mínimo possível para 20 cartões


def test_continuacao_nunca_vem_antes_do_comeco(r):
    nomes = [b.split(":")[0] for tela in r["continuacao"] for b in tela]
    assert nomes.index("B1") < nomes.index("B1 (continuação)")


def test_titular_formata_o_nome_de_urna_e_cita_o_tse(r):
    """Task 32: nome do TSE (maiúsculas) com iniciais maiúsculas; partícula no meio fica minúscula."""
    nomes = [t["nome"] for t in r["titulares"]]
    assert nomes == [
        "Eduardo Siqueira Campos",
        "Maria do Socorro",
        "Ismael Brito",
        "Da Silva e João-Paulo dos Anjos",
        "Zé",
    ]
    assert r["titulares"][0]["legenda"] == "Eleito(a) em 2024 · Fonte: TSE"
    assert r["titulares"][4]["legenda"] == "Fonte: TSE"  # ano inválido: não inventa o ano


def test_titular_ausente_ou_invalido_nao_vira_nome(r):
    assert r["titularInvalido"] == [None] * 8


def test_projecao_so_inclui_municipios_conhecidos_com_geometria(r):
    assert [f["cod"] for f in r["projecao"]] == ["1721000"]
    assert r["projecao"][0]["d"].startswith("M") and "NaN" not in r["projecao"][0]["d"]
