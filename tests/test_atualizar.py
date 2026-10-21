"""scripts/atualizar.py (Task 35, passo 7): a rotina diária ponta a ponta, sem rede (respostas reais gravadas)."""

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from src.coletores import siconfi
from src.orquestracao import estado as arquivo_estado
from src.orquestracao.fontes import FONTES
from src.orquestracao.painel import consolidar, instanciar

RAIZ = Path(__file__).parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("atualizar", RAIZ / "scripts" / "atualizar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(autouse=True)
def _ano_do_siconfi(monkeypatch):
    class Agora(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 14, tzinfo=UTC)

    monkeypatch.setattr(siconfi, "datetime", Agora)


@pytest.fixture
def arquivos(rede_gravada, tmp_path_factory):
    """painel_dados.json já publicado (as 9 fontes coletadas) + caminhos do estado."""
    pasta = tmp_path_factory.mktemp("dados")
    registros = {}
    for f in FONTES:
        c = instanciar(f)
        registros[f] = c.transformar(c.extrair())
    painel = pasta / "painel_dados.json"
    painel.write_text(json.dumps(consolidar(None, registros, "2026-10-21T12:00:00+00:00")), "utf-8")
    return painel, pasta / "estado_fontes.json"


def _rodar(painel, estado, *extra):
    return _script().main(["--painel", str(painel), "--estado", str(estado), *extra])


def test_inicializar_cria_estado_valido_sem_coletar(arquivos, rede_gravada):
    painel, estado = arquivos
    antes = painel.read_bytes()
    rede_gravada.clear()
    assert _rodar(painel, estado, "--inicializar") == 0
    e = arquivo_estado.ler(estado)
    assert all(f["status"] == "ok" and f["marca_sentinela"] for f in e["fontes"].values())
    assert e["fontes"]["TO-TER-01"]["coletado_em"] == "2026-10-21T12:00:00Z"
    assert painel.read_bytes() == antes
    assert not [
        u for u in rede_gravada if "/variaveis/" in u or "consulta_cand" in u
    ]  # só sentinelas


def test_rotina_diaria_sem_novidade_nao_toca_no_painel(arquivos, rede_gravada, capsys):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    antes = painel.read_bytes()
    rede_gravada.clear()
    assert _rodar(painel, estado) == 0
    assert painel.read_bytes() == antes
    assert capsys.readouterr().out.count("sem novidade") == 9
    assert not [u for u in rede_gravada if "/variaveis/" in u or "consulta_cand" in u]
    assert arquivo_estado.ler(estado)["fontes"]["TO-TER-01"]["status"] == "ok"


def test_forcar_uma_fonte_coleta_so_ela_e_regrava_o_painel(arquivos, rede_gravada):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    rede_gravada.clear()
    assert _rodar(painel, estado, "--forcar", "TO-TER-04") == 0
    dados = [u for u in rede_gravada if "/variaveis/" in u]
    assert len(dados) == 1 and "/agregados/4714/" in dados[0]
    novo = json.loads(painel.read_text("utf-8"))
    assert novo["fontes"]["TO-TER-04"]["coletado_em"] != "2026-10-21T12:00:00+00:00"
    assert novo["fontes"]["TO-TER-01"]["coletado_em"] == "2026-10-21T12:00:00+00:00"
    assert (
        arquivo_estado.ler(estado)["fontes"]["TO-TER-04"]["coletado_em"] != "2026-10-21T12:00:00Z"
    )


def test_forcar_todas_coleta_as_9(arquivos, capsys):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    assert _rodar(painel, estado, "--forcar", "todas") == 0
    assert capsys.readouterr().out.count("coletada (") == 9


@pytest.mark.parametrize(
    "valor", ["TO-XXX-99", "TO-TER-01,outra", "--todas", "todas,TO-TER-01", ";rm -rf /"]
)
def test_forcar_so_aceita_ids_conhecidos_ou_todas(arquivos, valor, capsys):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    antes = (painel.read_bytes(), estado.read_bytes())
    assert _rodar(painel, estado, f"--forcar={valor}") == 2
    assert (painel.read_bytes(), estado.read_bytes()) == antes
    assert "desconhecida" in capsys.readouterr().err


def test_forcar_varias_separadas_por_virgula(arquivos, capsys):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    assert _rodar(painel, estado, "--forcar", "TO-TER-04,TO-TER-06") == 0
    assert capsys.readouterr().out.count("coletada (") == 2


def test_estado_inexistente_ou_invalido_para_com_codigo_2(arquivos, capsys):
    painel, estado = arquivos
    assert _rodar(painel, estado) == 2 and "inicializar" in capsys.readouterr().err
    estado.write_text('{"versao": 9}', "utf-8")
    assert _rodar(painel, estado) == 2


def test_fonte_com_falha_nao_derruba_a_rotina_e_fica_registrada(arquivos, monkeypatch, capsys):
    painel, estado = arquivos
    _rodar(painel, estado, "--inicializar")
    modulo = _script()
    original = modulo.coletar

    def coletar(id_fonte):
        if id_fonte == "TO-TER-05":
            raise OSError("fora do ar")
        return original(id_fonte)

    monkeypatch.setattr(modulo, "coletar", coletar)
    antes = painel.read_bytes()
    assert (
        modulo.main(["--painel", str(painel), "--estado", str(estado), "--forcar", "TO-TER-05"])
        == 0
    )
    f = arquivo_estado.ler(estado)["fontes"]["TO-TER-05"]
    assert f["status"] == "erro" and f["falhas_consecutivas"] == 1
    assert painel.read_bytes() == antes  # nada aceito: o painel segue como estava
