"""Situação das fontes no rodapé (Task 36): src/ui/painel-logica.js executado no Node, com o estado_fontes.json real."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from src.orquestracao.fontes import FONTES

RAIZ = Path(__file__).parents[2]
MODULO = RAIZ / "src" / "ui" / "painel-logica.js"

SCRIPT = """
const L = require(process.argv[1]);
const real = JSON.parse(process.argv[2]);
const com = (id, campos) => ({ ...real, fontes: { ...real.fontes, [id]: { ...real.fontes[id], ...campos } } });
const ruim = [null, undefined, "x", [], {}, { fontes: {} }, { ultima_execucao_orquestrador: "ontem", fontes: {} },
  { ultima_execucao_orquestrador: "2026-10-21T17:00:00Z" }, { ultima_execucao_orquestrador: 5, fontes: {} }];
console.log(JSON.stringify({
  real: L.situacaoFontes(real),
  erro: L.situacaoFontes(com("TO-TER-05", { status: "erro", mensagem_erro: "OSError: fora do ar" })),
  suspeito: L.situacaoFontes(com("TO-TER-03", { status: "suspeito", mensagem_erro: "variação de +900% fora de 3σ" })),
  defasado: L.situacaoFontes(com("TO-REC-02", { status: "defasado" })),
  statusInventado: L.situacaoFontes(com("TO-TER-01", { status: "<img src=x onerror=alert(1)>" })),
  mensagemLonga: L.situacaoFontes(com("TO-TER-01", { status: "erro", mensagem_erro: "x".repeat(900) })),
  mensagemNoOk: L.situacaoFontes(com("TO-TER-01", { status: "ok", mensagem_erro: "resto de um erro antigo" })),
  semUmaFonte: L.situacaoFontes({ ...real, fontes: Object.fromEntries(Object.entries(real.fontes).filter(([k]) => k !== "TO-TER-04")) }),
  invalidos: ruim.map(L.situacaoFontes),
  horario: [
    L.situacaoFontes({ ...real, ultima_execucao_orquestrador: "2026-10-21T17:00:00Z" }).verificado,
    L.situacaoFontes({ ...real, ultima_execucao_orquestrador: "2026-12-31T23:30:00Z" }).verificado,
    L.situacaoFontes({ ...real, ultima_execucao_orquestrador: "2027-01-01T02:59:00Z" }).verificado,
  ],
  trimestre: L.situacaoFontes(com("TO-TER-07", { ultimo_periodo_coletado: "202601" })).itens.find((i) => i.id === "TO-TER-07").periodo,
  semPeriodo: L.situacaoFontes(com("TO-TER-07", { ultimo_periodo_coletado: null })).itens.find((i) => i.id === "TO-TER-07").periodo,
}));
"""


@pytest.fixture(scope="module")
def r():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node não instalado")
    real = (RAIZ / "src" / "ui" / "data" / "estado_fontes.json").read_text("utf-8")
    comando = [node, "-e", SCRIPT, str(MODULO), real]  # comando fixo, sem entrada externa
    saida = subprocess.run(comando, capture_output=True, text=True, check=True, timeout=30)  # noqa: S603
    return json.loads(saida.stdout)


def _item(situacao, id_fonte):
    return next(i for i in situacao["itens"] if i["id"] == id_fonte)


def test_as_9_fontes_do_catalogo_aparecem_na_ordem_do_catalogo(r):
    assert [i["id"] for i in r["real"]["itens"]] == FONTES


def test_estado_real_mostra_tudo_atualizado_e_o_horario_de_brasilia(r):
    s = r["real"]
    assert s["todasOk"] is True and s["resumo"] == "9 de 9 fontes atualizadas"
    assert all(i["statusRotulo"] == "Atualizada" and i["temMensagem"] is False for i in s["itens"])
    assert " às " in s["verificado"] and s["verificado"][:2].isdigit()


def test_horario_e_convertido_de_utc_para_brasilia(r):
    assert r["horario"] == [
        "21/10/2026 às 14:00",
        "31/12/2026 às 20:30",
        "31/12/2026 às 23:59",  # 02:59 UTC de 01/01 ainda é 31/12 em Brasília
    ]


@pytest.mark.parametrize(
    ("chave", "id_fonte", "rotulo", "icone"),
    [
        ("erro", "TO-TER-05", "Com falha", "ph-warning"),
        ("suspeito", "TO-TER-03", "Em análise", "ph-magnifying-glass"),
        ("defasado", "TO-REC-02", "Defasada", "ph-clock-countdown"),
    ],
)
def test_fonte_com_problema_tem_texto_e_icone_proprios(r, chave, id_fonte, rotulo, icone):
    s = r[chave]
    item = _item(s, id_fonte)
    assert (item["statusRotulo"], item["icone"]) == (rotulo, icone)
    assert s["todasOk"] is False and s["resumo"] == "8 de 9 fontes atualizadas, 1 com atenção"
    assert all(i["statusRotulo"] == "Atualizada" for i in s["itens"] if i["id"] != id_fonte)


def test_mensagem_do_erro_aparece_so_quando_a_fonte_nao_esta_ok(r):
    assert _item(r["erro"], "TO-TER-05")["mensagem"] == "OSError: fora do ar"
    assert _item(r["suspeito"], "TO-TER-03")["mensagem"].endswith("fora de 3σ")
    assert (
        _item(r["mensagemNoOk"], "TO-TER-01")["temMensagem"] is False
    )  # resto de erro antigo não aparece
    assert len(_item(r["mensagemLonga"], "TO-TER-01")["mensagem"]) == 300


def test_status_desconhecido_vira_falha_e_nunca_e_repassado(r):
    item = _item(r["statusInventado"], "TO-TER-01")
    assert item["status"] == "erro" and item["statusRotulo"] == "Com falha"
    assert "<img" not in json.dumps(item)


def test_fonte_ausente_do_arquivo_aparece_como_falha_e_nao_some(r):
    item = _item(r["semUmaFonte"], "TO-TER-04")
    assert item["statusRotulo"] == "Com falha" and item["periodo"] == "sem dado"
    assert len(r["semUmaFonte"]["itens"]) == 9


def test_periodo_trimestral_e_legivel(r):
    assert r["trimestre"] == "1º trim. 2026" and r["semPeriodo"] == "sem dado"
    assert _item(r["real"], "TO-TER-07")["periodo"] == "2º trim. 2026"


def test_arquivo_invalido_devolve_null_e_o_painel_segue_sem_a_linha(r):
    assert r["invalidos"] == [None] * 9


def test_index_nao_depende_de_cdn_nem_de_terceiros():
    html = (RAIZ / "index.html").read_text("utf-8")
    assert "unpkg" not in html and "googleapis" not in html and "gstatic" not in html
    assert (
        "./src/ui/vendor/phosphor/style.css" in html and "./src/ui/vendor/inter/fonts.css" in html
    )


def test_aviso_legal_dos_titulares_esta_no_rodape():
    html = (RAIZ / "index.html").read_text("utf-8")
    for trecho in (
        "Tribunal Superior Eleitoral",
        "cargos públicos eletivos",
        "Lei de Acesso à Informação",
    ):
        assert trecho in html


def test_index_tem_csp_so_do_proprio_site():
    """O Pages não deixa configurar cabeçalhos: a CSP vai por meta. Nada de host externo nem script inline."""
    html = (RAIZ / "index.html").read_text("utf-8")
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', html)
    assert m, "index.html sem Content-Security-Policy"
    politica = dict(d.strip().split(" ", 1) for d in m.group(1).split(";") if d.strip())
    assert politica["default-src"] == "'none'"
    assert politica["connect-src"] == "'self'" and politica["font-src"] == "'self'"
    assert (
        politica["script-src"] == "'self' 'unsafe-eval'"
    )  # o runtime x-dc precisa do eval; nada de 'unsafe-inline'
    assert "unsafe-inline" not in politica["script-src"]
    assert not re.search(r"https?:|\*", m.group(1))  # nenhum host externo, nenhum curinga
