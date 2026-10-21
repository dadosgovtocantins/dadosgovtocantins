"""Alertas por issue: quando abrir, quando fechar e o que o script manda para o `gh` (simulado)."""

import importlib.util
import json
from pathlib import Path

import pytest
from src.orquestracao.estado import estado_vazio
from src.orquestracao.issues import ROTULO, Acao, fonte_da_issue, planejar, titulo

RAIZ = Path(__file__).parents[2]


def _estado(**mudancas):
    e = estado_vazio()
    for f in e["fontes"].values():
        f.update(status="ok", falhas_consecutivas=0, mensagem_erro=None)
    for fonte, campos in mudancas.items():
        e["fontes"][fonte.replace("_", "-").upper()].update(campos)
    return e


def test_uma_falha_so_nao_abre_issue():
    assert planejar(_estado(to_ter_01={"status": "erro", "falhas_consecutivas": 1}), []) == []


@pytest.mark.parametrize("status", ["erro", "suspeito"])
def test_duas_falhas_seguidas_abrem_a_issue(status):
    (acao,) = planejar(
        _estado(
            to_ter_01={"status": status, "falhas_consecutivas": 2, "mensagem_erro": "OSError: x"}
        ),
        [],
    )
    assert (acao.tipo, acao.fonte, acao.titulo) == ("abrir", "TO-TER-01", titulo("TO-TER-01"))
    assert "OSError: x" in acao.corpo and status in acao.corpo


def test_defasada_abre_mesmo_sem_falhas_contadas():
    assert [a.tipo for a in planejar(_estado(to_rec_02={"status": "defasado"}), [])] == ["abrir"]


def test_nao_duplica_issue_ja_aberta():
    e = _estado(to_ter_01={"status": "erro", "falhas_consecutivas": 5})
    assert planejar(e, [{"number": 7, "title": titulo("TO-TER-01")}]) == []


def test_fecha_quando_a_fonte_volta_a_ok():
    abertas = [{"number": 7, "title": titulo("TO-TER-01")}]
    assert planejar(_estado(), abertas) == [Acao("fechar", "TO-TER-01", numero=7)]


def test_issue_de_fonte_ainda_com_problema_nao_fecha():
    e = _estado(to_ter_01={"status": "erro", "falhas_consecutivas": 1})
    assert planejar(e, [{"number": 7, "title": titulo("TO-TER-01")}]) == []


def test_issue_de_outro_assunto_e_ignorada():
    assert planejar(_estado(), [{"number": 3, "title": "Dúvida sobre o painel"}]) == []


def test_fonte_da_issue():
    assert fonte_da_issue(titulo("TO-REC-02")) == "TO-REC-02"
    assert fonte_da_issue("qualquer coisa") is None


# --- script ---------------------------------------------------------------------------------------


def _script():
    spec = importlib.util.spec_from_file_location(
        "sincronizar", RAIZ / "scripts" / "sincronizar_issues.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class GhFalso:
    def __init__(self, abertas):
        self.abertas, self.chamadas = abertas, []

    def __call__(self, *args):
        self.chamadas.append(args)
        return json.dumps(self.abertas) if args[:2] == ("issue", "list") else ""


def test_script_abre_e_fecha_pelo_gh():
    gh = GhFalso([{"number": 9, "title": titulo("TO-TER-02")}])
    e = _estado(to_ter_01={"status": "erro", "falhas_consecutivas": 2, "mensagem_erro": "x"})
    feitas = _script().sincronizar(e, gh)
    assert len(feitas) == 2
    comandos = [c[:2] for c in gh.chamadas]
    assert ("issue", "create") in comandos and ("issue", "close") in comandos
    criar = next(c for c in gh.chamadas if c[:2] == ("issue", "create"))
    assert ROTULO in criar and titulo("TO-TER-01") in criar
    assert next(c for c in gh.chamadas if c[:2] == ("issue", "close"))[2] == "9"


def test_script_simular_so_lista_e_nao_escreve():
    gh = GhFalso([])
    e = _estado(to_ter_01={"status": "erro", "falhas_consecutivas": 3})
    assert len(_script().sincronizar(e, gh, simular=True)) == 1
    assert [c[:2] for c in gh.chamadas] == [("issue", "list")]


def test_script_sem_nada_a_fazer_so_consulta():
    gh = GhFalso([])
    assert _script().sincronizar(_estado(), gh) == []
    assert len(gh.chamadas) == 1
