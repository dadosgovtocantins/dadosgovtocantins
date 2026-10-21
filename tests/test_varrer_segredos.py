"""
scripts/varrer_segredos.sh (Task 34): a guarda do e-mail de infraestrutura e a chamada do gitleaks.
Roda em repositórios descartáveis, com um padrão FALSO e um gitleaks falso: nunca usa o padrão real.
"""

import os
import subprocess
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "varrer_segredos.sh"
PADRAO = r"segredo-falso@exemplo\.invalid"
ENDERECO = "segredo-falso@exemplo.invalid"
AMBIENTE_GIT = {
    "GIT_AUTHOR_NAME": "Teste",
    "GIT_AUTHOR_EMAIL": "teste@exemplo.invalid",
    "GIT_COMMITTER_NAME": "Teste",
    "GIT_COMMITTER_EMAIL": "teste@exemplo.invalid",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603
        ["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args],  # noqa: S607
        check=True,
        capture_output=True,
        env={**os.environ, **AMBIENTE_GIT},
        timeout=60,
    )


def _gitleaks_falso(pasta: Path, codigo_saida: int) -> Path:
    falso = pasta / "gitleaks-falso"
    falso.write_text(f"#!/bin/sh\nexit {codigo_saida}\n", "utf-8")
    falso.chmod(0o755)
    return falso


def _repositorio(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("projeto limpo\n", "utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "limpo")
    return repo


def _varrer(repo: Path, gitleaks: Path | None, padrao: str | None = PADRAO):
    env = {k: v for k, v in os.environ.items() if k != "PADRAO_EMAIL_INFRA"}
    env["HOME"] = str(repo.parent)  # sem o arquivo local do padrão real
    if padrao:
        env["PADRAO_EMAIL_INFRA"] = padrao
    if gitleaks:
        env["GITLEAKS_BIN"] = str(gitleaks)
    return subprocess.run(  # noqa: S603
        ["/bin/bash", str(SCRIPT)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.fixture
def repo(tmp_path):
    return _repositorio(tmp_path)


def test_repositorio_limpo_passa(repo, tmp_path):
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0))
    assert r.returncode == 0, r.stderr
    assert "APROVADO" in r.stdout


def test_sem_padrao_define_erro_e_nao_varre(repo, tmp_path):
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0), padrao=None)
    assert r.returncode == 2 and "PADRAO_EMAIL_INFRA" in r.stderr


def test_padrao_em_arquivo_novo_ainda_nao_commitado_reprova(repo, tmp_path):
    (repo / "nota.md").write_text(f"contato: {ENDERECO}\n", "utf-8")
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0))
    assert r.returncode == 1 and "nota.md" in r.stderr
    assert ENDERECO not in r.stdout + r.stderr  # nunca imprime o conteúdo


def test_padrao_so_no_historico_reprova_mesmo_apagado_da_arvore(repo, tmp_path):
    """O caso que motivou a task: o arquivo foi corrigido, mas o commit antigo ainda tem o e-mail."""
    (repo / "nota.md").write_text(f"contato: {ENDERECO}\n", "utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "adiciona")
    (repo / "nota.md").write_text("contato removido\n", "utf-8")
    _git(repo, "commit", "-q", "-am", "remove")
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0))
    assert r.returncode == 1 and "commit(s) do histórico" in r.stderr


def test_padrao_no_autor_do_commit_reprova(repo, tmp_path):
    (repo / "a.txt").write_text("x\n", "utf-8")
    _git(repo, "add", "-A")
    subprocess.run(  # noqa: S603
        ["git", "-C", str(repo), "commit", "-q", "-m", "autor"],  # noqa: S607
        check=True,
        capture_output=True,
        env={**os.environ, **AMBIENTE_GIT, "GIT_AUTHOR_EMAIL": ENDERECO},
        timeout=60,
    )
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0))
    assert r.returncode == 1 and "metadados de commit" in r.stderr


def test_padrao_dentro_de_pptx_reprova(repo, tmp_path):
    """O .pptx é um zip: o grep direto não enxerga o texto dentro dele."""
    with zipfile.ZipFile(repo / "slides.pptx", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ppt/slides/slide1.xml", f"<a:t>{ENDERECO}</a:t>")
    r = _varrer(repo, _gitleaks_falso(tmp_path, 0))
    assert r.returncode == 1 and "slides.pptx" in r.stderr


def test_gitleaks_que_acha_segredo_reprova(repo, tmp_path):
    r = _varrer(repo, _gitleaks_falso(tmp_path, 1))
    assert r.returncode == 1 and "gitleaks encontrou segredo" in r.stderr


def test_gitleaks_ausente_reprova(repo, tmp_path):
    r = _varrer(repo, tmp_path / "nao-existe")
    assert r.returncode == 1
