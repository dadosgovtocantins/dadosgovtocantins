"""Publicação incremental do site (Task 36): scripts/publicar_site.sh contra um repositório remoto LOCAL."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).parents[1]
SCRIPT = RAIZ / "scripts" / "publicar_site.sh"
ARQUIVOS_RAIZ = ("index.html", "support.js", "tocantins_municipios_regioes.geojson")
BASH = shutil.which("bash")
GIT = shutil.which("git")

pytestmark = pytest.mark.skipif(not (BASH and GIT), reason="precisa de bash e git")


def _git(*args, cwd=None, env=None):
    return subprocess.run(  # noqa: S603
        [GIT, *args], cwd=cwd, env=env, capture_output=True, text=True, check=True, timeout=60
    )


@pytest.fixture
def ambiente(monkeypatch):
    """Git isolado da configuração do computador (assinatura, hooks, identidade global)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        PYTHON=sys.executable,
        PADRAO_EMAIL_INFRA="nada-disso-aparece-no-site",
        HOME=str(Path(os.devnull).parent),
    )
    return env


@pytest.fixture
def projeto(tmp_path):
    """Cópia do projeto com o que o montador usa: os dados mudam aqui, nunca no projeto de verdade."""
    p = tmp_path / "projeto"
    shutil.copytree(RAIZ / "src", p / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (p / "scripts").mkdir()
    for nome in ("montar_site.py", "publicar_site.sh"):
        shutil.copy2(RAIZ / "scripts" / nome, p / "scripts" / nome)
    for nome in ARQUIVOS_RAIZ:
        shutil.copy2(RAIZ / nome, p / nome)
    (p / "bandeiras").mkdir()
    for bandeira in sorted((RAIZ / "bandeiras").glob("*.webp"))[:2]:
        shutil.copy2(bandeira, p / "bandeiras" / bandeira.name)
    return p


@pytest.fixture
def remoto(tmp_path, ambiente):
    """Repositório público vazio (novo, como `dadosgovtocantins/painel` recém-criado)."""
    r = tmp_path / "publico.git"
    _git("init", "--bare", "--quiet", "-b", "main", str(r), env=ambiente)
    return r


def _publicar(projeto, remoto, ambiente, **extra):
    env = {**ambiente, **extra}
    return subprocess.run(  # noqa: S603
        [BASH, str(projeto / "scripts" / "publicar_site.sh"), str(remoto), "main"],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _commits(remoto, ambiente):
    saida = _git("--git-dir", str(remoto), "log", "--format=%H", "main", env=ambiente).stdout
    return saida.split()


def _arquivos(remoto, ambiente, commit="main"):
    return set(
        _git(
            "--git-dir", str(remoto), "ls-tree", "-r", "--name-only", commit, env=ambiente
        ).stdout.split()
    )


def test_primeira_publicacao_cria_o_site_inteiro_num_repositorio_vazio(projeto, remoto, ambiente):
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode == 0, r.stderr
    assert len(_commits(remoto, ambiente)) == 1
    arquivos = _arquivos(remoto, ambiente)
    assert {"index.html", "support.js", ".nojekyll", "src/ui/data/estado_fontes.json"} <= arquivos
    assert not [
        a
        for a in arquivos
        if a.endswith(".py") or a.startswith(("tests/", ".planning/", "scripts/"))
    ]


def test_o_commit_e_do_robo_e_sem_o_email_da_conta_de_infraestrutura(projeto, remoto, ambiente):
    _publicar(projeto, remoto, ambiente)
    autor = _git(
        "--git-dir", str(remoto), "log", "-1", "--format=%an <%ae>", "main", env=ambiente
    ).stdout.strip()
    assert autor == "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>"


def test_sem_mudanca_nao_cria_commit(projeto, remoto, ambiente):
    _publicar(projeto, remoto, ambiente)
    antes = _commits(remoto, ambiente)
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode == 0 and "Nada a publicar" in r.stdout
    assert _commits(remoto, ambiente) == antes


def test_mudanca_so_no_estado_gera_um_commit_que_toca_so_esse_arquivo(projeto, remoto, ambiente):
    _publicar(projeto, remoto, ambiente)
    estado = projeto / "src" / "ui" / "data" / "estado_fontes.json"
    dados = json.loads(estado.read_text("utf-8"))
    dados["ultima_execucao_orquestrador"] = "2026-10-22T17:00:07Z"
    estado.write_text(json.dumps(dados, indent=2) + "\n", "utf-8")
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode == 0, r.stderr
    commits = _commits(remoto, ambiente)
    assert len(commits) == 2
    tocados = _git(
        "--git-dir", str(remoto), "show", "--name-only", "--format=", commits[0], env=ambiente
    ).stdout.split()
    assert tocados == ["src/ui/data/estado_fontes.json"]  # bandeiras e GeoJSON não foram regravados


def test_arquivo_que_saiu_da_lista_e_removido_do_site_publico(projeto, remoto, ambiente):
    _publicar(projeto, remoto, ambiente)
    bandeira = next((projeto / "bandeiras").iterdir())
    bandeira.unlink()
    assert _publicar(projeto, remoto, ambiente).returncode == 0
    assert f"bandeiras/{bandeira.name}" not in _arquivos(remoto, ambiente)


def test_segredo_no_site_aborta_antes_de_publicar_qualquer_coisa(projeto, remoto, ambiente):
    chave = (
        "AKIA" + "ABCDEFGHIJKLMNOP"
    )  # montada na execução: o repositório não guarda nada com cara de segredo
    (projeto / "index.html").write_text((projeto / "index.html").read_text("utf-8") + chave)
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode != 0 and "chave da AWS" in r.stderr
    assert chave not in r.stdout + r.stderr
    assert _git("--git-dir", str(remoto), "branch", "--list", env=ambiente).stdout.strip() == ""


def test_sem_o_padrao_do_email_a_publicacao_e_recusada(projeto, remoto, ambiente):
    env = {k: v for k, v in ambiente.items() if k != "PADRAO_EMAIL_INFRA"}
    r = subprocess.run(  # noqa: S603
        [BASH, str(projeto / "scripts" / "publicar_site.sh"), str(remoto)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode != 0 and "padrão do e-mail" in r.stderr
    assert _git("--git-dir", str(remoto), "branch", "--list", env=ambiente).stdout.strip() == ""


def test_repositorio_inexistente_falha_com_mensagem_clara(projeto, tmp_path, ambiente):
    r = _publicar(projeto, tmp_path / "nao-existe.git", ambiente)
    assert r.returncode != 0 and "clonar" in r.stderr


def test_token_nunca_aparece_na_saida(projeto, remoto, ambiente):
    token = "token-de-teste-" + "x" * 20
    r = _publicar(projeto, remoto, ambiente, PAT_PUBLICACAO_PAINEL=token)
    assert r.returncode == 0
    assert token not in r.stdout + r.stderr


def test_script_nao_usa_force_nem_depuracao_nem_token_na_url():
    texto = SCRIPT.read_text("utf-8")
    codigo = "\n".join(linha for linha in texto.splitlines() if not linha.lstrip().startswith("#"))
    assert "--force" not in codigo and "+HEAD" not in codigo and "-f " not in codigo
    assert "set -x" not in codigo and "set -o xtrace" not in codigo
    assert (
        "x-access-token:@" not in codigo and "https://${" not in codigo
    )  # token só no cabeçalho do Git
    assert 'export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic' in codigo


def test_workflow_so_publica_com_o_segredo_e_nunca_cancela():
    wf = (RAIZ / ".github" / "workflows" / "verificar.yml").read_text("utf-8")
    assert "PAT_PUBLICACAO_PAINEL" in wf and "Publicação desligada" in wf
    assert "cancel-in-progress: false" in wf
