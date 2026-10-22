"""Publicação incremental do site (Task 36): scripts/publicar_site.sh contra um repositório remoto LOCAL."""

import base64
import hashlib
import json
import os
import re
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
    for nome in ("montar_site.py", "publicar_site.sh", "github_known_hosts"):
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


# --- falhas nunca viram "publicado" ------------------------------------------------------------------


def _hook(remoto, corpo):
    h = remoto / "hooks" / "pre-receive"
    h.write_text("#!/bin/sh\n" + corpo + "\n")
    h.chmod(0o755)


def test_push_recusado_pelo_remoto_falha_e_nao_diz_que_publicou(projeto, remoto, ambiente):
    """Caso real (22/10/2026): token sem permissão de escrita. O script antes imprimia "Site publicado"."""
    _hook(remoto, "echo 'sem permissao' >&2; exit 1")
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode != 0
    assert "Site publicado" not in r.stdout + r.stderr
    assert "push foi recusado" in r.stderr and "nada foi publicado" in r.stderr
    assert _git("--git-dir", str(remoto), "branch", "--list", env=ambiente).stdout.strip() == ""


def _mudar_estado(projeto, quando):
    estado = projeto / "src" / "ui" / "data" / "estado_fontes.json"
    dados = json.loads(estado.read_text("utf-8"))
    dados["ultima_execucao_orquestrador"] = quando
    estado.write_text(json.dumps(dados, indent=2) + "\n", "utf-8")


def test_push_recusado_uma_vez_em_ramo_existente_atualiza_e_tenta_de_novo(
    projeto, remoto, ambiente
):
    _publicar(projeto, remoto, ambiente)
    _mudar_estado(projeto, "2026-10-23T17:00:00Z")
    _hook(remoto, 'if [ ! -f "$GIT_DIR/ja_recusou" ]; then touch "$GIT_DIR/ja_recusou"; exit 1; fi')
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode == 0, r.stderr
    assert "tentando uma vez mais" in r.stderr and "Site publicado" in r.stdout
    assert len(_commits(remoto, ambiente)) == 2


def test_push_recusado_sempre_em_ramo_existente_falha_apos_a_segunda_tentativa(
    projeto, remoto, ambiente
):
    _publicar(projeto, remoto, ambiente)
    _mudar_estado(projeto, "2026-10-24T17:00:00Z")
    _hook(remoto, "exit 1")
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode != 0 and "Site publicado" not in r.stdout
    assert "recusado de novo" in r.stderr
    assert len(_commits(remoto, ambiente)) == 1


def test_script_nao_esconde_o_erro_do_push():
    codigo = "\n".join(
        linha
        for linha in SCRIPT.read_text("utf-8").splitlines()
        if not linha.lstrip().startswith("#")
    )
    assert "2>/dev/null" not in codigo.replace(
        "ls-remote --exit-code --heads origin", ""
    )  # só o teste de existência do ramo
    assert (
        'ls-remote origin "refs/heads/${RAMO}"' in codigo
    )  # confere no remoto antes de declarar sucesso


# --- autenticação por deploy key SSH -----------------------------------------------------------------

FINGERPRINT_ED25519_GITHUB = "+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"  # publicada pela GitHub


def test_known_hosts_traz_as_chaves_oficiais_da_github():
    linhas = (RAIZ / "scripts" / "github_known_hosts").read_text("utf-8").splitlines()
    assert sorted(linha.split()[1] for linha in linhas) == [
        "ecdsa-sha2-nistp256",
        "ssh-ed25519",
        "ssh-rsa",
    ]
    assert all(linha.startswith("github.com ") for linha in linhas)
    ed = next(linha for linha in linhas if " ssh-ed25519 " in linha).split()[2]
    digest = base64.b64encode(hashlib.sha256(base64.b64decode(ed)).digest()).decode().rstrip("=")
    assert digest == FINGERPRINT_ED25519_GITHUB


@pytest.fixture
def ssh_falso(tmp_path):
    """`ssh` de mentira no PATH: registra como foi chamado e confere a chave, depois falha (nada de rede)."""
    pasta = tmp_path / "bin"
    pasta.mkdir()
    log = tmp_path / "ssh.log"
    ssh = pasta / "ssh"
    ssh.write_text(
        "#!/bin/sh\n"
        f'echo "ARGS: $*" >> "{log}"\n'
        'while [ $# -gt 0 ]; do if [ "$1" = "-i" ]; then k="$2"; fi; shift; done\n'
        f'echo "CHAVE_EXISTE: $([ -f "$k" ] && echo sim || echo nao)" >> "{log}"\n'
        f'echo "CHAVE_0600: $([ -n "$(find "$k" -perm 600 2>/dev/null)" ] && echo sim || echo nao)" >> "{log}"\n'
        f'echo "CHAVE_CONTEUDO: $(cat "$k")" >> "{log}"\n'
        f'echo "CAMINHO: $k" >> "{log}"\n'
        "exit 255\n"
    )
    ssh.chmod(0o755)
    return pasta, log


def test_deploy_key_vai_para_arquivo_0600_com_servidor_verificado_e_e_apagada(
    projeto, remoto, ambiente, ssh_falso
):
    pasta, log = ssh_falso
    chave = (
        "-----BEGIN "
        + "OPENSSH PRIVATE KEY-----\nchave-falsa-de-teste\n-----END "
        + "OPENSSH PRIVATE KEY-----"
    )
    env = {**ambiente, "PATH": f"{pasta}:{ambiente['PATH']}", "PAINEL_DEPLOY_KEY": chave}
    r = subprocess.run(  # noqa: S603
        [
            BASH,
            str(projeto / "scripts" / "publicar_site.sh"),
            "git@github.com:dadosgovtocantins/painel.git",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode != 0 and "clonar" in r.stderr  # o ssh falso recusa: nada de rede
    registro = log.read_text("utf-8")
    assert "CHAVE_EXISTE: sim" in registro and "CHAVE_0600: sim" in registro
    assert "chave-falsa-de-teste" in registro  # a chave chegou ao ssh...
    assert "chave-falsa-de-teste" not in r.stdout + r.stderr  # ...e nunca à saída do script
    for opcao in (
        "StrictHostKeyChecking=yes",
        "IdentitiesOnly=yes",
        "IdentityAgent=none",
        "BatchMode=yes",
        "-F /dev/null",
    ):
        assert opcao in registro, opcao
    assert "github_known_hosts" in registro
    caminho = re.search(r"CAMINHO: (.+)", registro).group(1)
    assert not Path(caminho).exists()  # apagada ao sair


def test_sem_deploy_key_o_script_nao_mexe_na_configuracao_do_ssh(projeto, remoto, ambiente):
    r = _publicar(projeto, remoto, ambiente)
    assert r.returncode == 0, r.stderr  # remoto local: nada de SSH


def test_script_nao_usa_force_nem_depuracao_nem_desliga_a_verificacao_do_servidor():
    texto = SCRIPT.read_text("utf-8")
    codigo = "\n".join(linha for linha in texto.splitlines() if not linha.lstrip().startswith("#"))
    assert (
        "--force" not in codigo
        and "+HEAD" not in codigo
        and "-f " not in codigo.replace("-F /dev/null", "")
    )
    assert "set -x" not in codigo and "set -o xtrace" not in codigo
    assert (
        "StrictHostKeyChecking=no" not in codigo
        and "accept-new" not in codigo
        and "ssh-keyscan" not in codigo
    )
    assert "StrictHostKeyChecking=yes" in codigo and "github_known_hosts" in codigo
    assert (
        "umask 077" in codigo and "rm -rf" in codigo
    )  # arquivo da chave privado e apagado ao sair
    assert (
        'echo "${PAINEL_DEPLOY_KEY' not in codigo
        and "printf '%s\\n' \"${PAINEL_DEPLOY_KEY}\" >" in codigo
    )


def test_workflow_so_publica_com_o_segredo_da_deploy_key_e_nunca_cancela():
    wf = (RAIZ / ".github" / "workflows" / "verificar.yml").read_text("utf-8")
    assert "PAINEL_DEPLOY_KEY" in wf and "Publicação desligada" in wf
    assert "PAT_PUBLICACAO_PAINEL" not in wf
    assert "git@github.com:" in wf and "cancel-in-progress: false" in wf
