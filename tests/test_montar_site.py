"""Montagem do site público (Task 36): só a lista fixa, sem vazamento, incremental. Nada acessa a rede."""

import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest
from src.orquestracao import site
from src.orquestracao.site import ARQUIVOS, GERADOS, SiteInvalidoError, listar, montar

RAIZ = Path(__file__).parents[1]


@pytest.fixture(autouse=True)
def _sem_padrao_local(monkeypatch):
    """O padrão do e-mail de infraestrutura é do computador do Bruno: nos testes ele é sempre explícito."""
    monkeypatch.delenv("PADRAO_EMAIL_INFRA", raising=False)
    monkeypatch.setattr(site, "ARQUIVO_PADRAO", Path("/nao/existe/padrao"))


@pytest.fixture
def raiz(tmp_path):
    """Cópia mínima do projeto (lista fixa + 2 bandeiras) para os casos de recusa."""
    destino = tmp_path / "projeto"
    for rel in ARQUIVOS:
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / rel, destino / rel)
    shutil.copytree(RAIZ / "src" / "ui" / "vendor", destino / "src" / "ui" / "vendor")
    (destino / "bandeiras").mkdir()
    for bandeira in sorted((RAIZ / "bandeiras").glob("*.webp"))[:2]:
        shutil.copy2(bandeira, destino / "bandeiras" / bandeira.name)
    return destino


def _saida(tmp_path):
    return tmp_path / "saida"


def _tudo(pasta: Path) -> dict[str, bytes]:
    return {
        p.relative_to(pasta).as_posix(): p.read_bytes() for p in pasta.rglob("*") if p.is_file()
    }


def _editar(raiz, rel, trocar):
    arq = raiz / rel
    arq.write_bytes(trocar(arq.read_bytes()))


# --- o site de verdade ----------------------------------------------------------------------------


def test_site_real_tem_exatamente_a_lista_fixa_e_os_gerados(tmp_path):
    montar(_saida(tmp_path))
    assert set(_tudo(_saida(tmp_path))) == set(listar()) | set(GERADOS)


def test_site_real_nao_leva_codigo_testes_planejamento_nem_dado_antigo(tmp_path):
    montar(_saida(tmp_path))
    caminhos = set(_tudo(_saida(tmp_path)))
    proibidos = (
        "tests/",
        ".planning/",
        "scripts/",
        "docs/",
        ".github/",
        "infra/",
        ".data_raw/",
        "data/",
    )
    assert not [c for c in caminhos if c.startswith(proibidos)]
    assert not [
        c for c in caminhos if c.endswith((".py", ".md", ".pptx", ".env", ".pem", ".csv", ".db"))
    ]
    assert "src/ui/data/dados_coletados_real.json" not in caminhos  # dados simulados antigos
    assert "index-antigo.html" not in caminhos and "CLAUDE.md" not in caminhos


def test_site_real_cabe_no_pages_e_a_pasta_de_vendor_leva_as_licencas(tmp_path):
    montar(_saida(tmp_path))
    tudo = _tudo(_saida(tmp_path))
    assert sum(len(v) for v in tudo.values()) < 8 * 1024 * 1024
    for lic in ("inter/LICENSE.txt", "phosphor/LICENSE", "react/LICENSE"):
        assert f"src/ui/vendor/{lic}" in tudo


def test_dados_do_site_sao_os_do_projeto(tmp_path):
    montar(_saida(tmp_path))
    tudo = _tudo(_saida(tmp_path))
    for rel in ARQUIVOS:
        assert tudo[rel] == (RAIZ / rel).read_bytes(), rel


def test_segunda_montagem_nao_reescreve_nada(tmp_path):
    montar(_saida(tmp_path))
    r = montar(_saida(tmp_path))
    assert (r["escritos"], r["removidos"]) == (0, 0) and r["iguais"] == len(listar()) + len(GERADOS)


def test_so_o_arquivo_que_mudou_e_reescrito(tmp_path, raiz):
    saida = _saida(tmp_path)
    montar(saida, raiz)
    antes = _tudo(saida)
    _editar(
        raiz, "src/ui/data/estado_fontes.json", lambda b: b.replace(b'"ok"', b'"ok"', 1) + b"\n"
    )
    r = montar(saida, raiz)
    assert (r["escritos"], r["removidos"]) == (1, 0)
    depois = _tudo(saida)
    assert [k for k in depois if depois[k] != antes[k]] == ["src/ui/data/estado_fontes.json"]


# --- lista estrita ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nome", ["leia-me.txt", "script.py", ".env", "chave.pem", "dados.json", "bandeira.png"]
)
def test_arquivo_fora_da_lista_em_pasta_liberada_e_erro_e_nada_e_copiado(tmp_path, raiz, nome):
    (raiz / "bandeiras" / nome).write_bytes(b"x")
    with pytest.raises(SiteInvalidoError, match="fora da lista"):
        montar(_saida(tmp_path), raiz)
    assert not _saida(tmp_path).exists()


def test_arquivo_novo_na_raiz_ou_em_src_nao_entra_sem_ser_colocado_na_lista(tmp_path, raiz):
    (raiz / "segredo.html").write_text("x")
    (raiz / "src" / "ui" / "novo.js").write_text("x")
    montar(_saida(tmp_path), raiz)
    assert "segredo.html" not in _tudo(_saida(tmp_path)) and "src/ui/novo.js" not in _tudo(
        _saida(tmp_path)
    )


def test_ds_store_do_mac_e_ignorado(tmp_path, raiz):
    (raiz / "bandeiras" / ".DS_Store").write_bytes(b"\x00")
    montar(_saida(tmp_path), raiz)
    assert ".DS_Store" not in "".join(_tudo(_saida(tmp_path)))


@pytest.mark.parametrize(
    "rel", ["index.html", "src/ui/data/painel_dados.json", "src/ui/data/estado_fontes.json"]
)
def test_arquivo_da_lista_ausente_derruba_a_montagem(tmp_path, raiz, rel):
    (raiz / rel).unlink()
    with pytest.raises(SiteInvalidoError, match="não existe"):
        montar(_saida(tmp_path), raiz)
    assert not _saida(tmp_path).exists()


def test_pasta_liberada_ausente_derruba_a_montagem(tmp_path, raiz):
    shutil.rmtree(raiz / "bandeiras")
    with pytest.raises(SiteInvalidoError, match="pasta da lista"):
        montar(_saida(tmp_path), raiz)


# --- vazamentos --------------------------------------------------------------------------------------

# Montados em tempo de execução: o próprio repositório não pode conter nada com cara de segredo (gitleaks).
SEGREDOS_FALSOS = {
    "chave privada": "-----BEGIN " + "RSA PRIVATE KEY-----",
    "chave da AWS": "AKIA" + "ABCDEFGHIJKLMNOP",
    "token do GitHub": "ghp" + "_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
    "chave de API do Google": "AIza" + "SyA1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q",
    "conta de infraestrutura": "dadosgovtocantins" + "@" + "exemplo.test",
}


@pytest.mark.parametrize("tipo", list(SEGREDOS_FALSOS))
@pytest.mark.parametrize(
    "rel", ["index.html", "src/ui/data/painel_indicadores.json", "bandeiras/ou-qualquer.webp"]
)
def test_segredo_em_qualquer_arquivo_recusa_a_montagem_sem_vazar_o_conteudo(
    tmp_path, raiz, tipo, rel
):
    if rel.startswith("bandeiras/"):
        rel = "bandeiras/" + next((raiz / "bandeiras").iterdir()).name
    _editar(raiz, rel, lambda b: b + b"\n" + SEGREDOS_FALSOS[tipo].encode())
    with pytest.raises(SiteInvalidoError) as erro:
        montar(_saida(tmp_path), raiz)
    texto = str(erro.value)
    assert rel in texto and tipo in texto
    assert SEGREDOS_FALSOS[tipo] not in texto
    assert not _saida(tmp_path).exists()


def test_padrao_do_email_de_infraestrutura_barra_o_arquivo_e_nao_aparece_na_mensagem(
    tmp_path, raiz
):
    padrao = re.compile(rb"meu-padrao-secreto-\d+")
    _editar(raiz, "index.html", lambda b: b + b"<!-- meu-padrao-secreto-123 -->")
    with pytest.raises(SiteInvalidoError) as erro:
        montar(_saida(tmp_path), raiz, padrao)
    assert "index.html" in str(erro.value) and "meu-padrao-secreto" not in str(erro.value)


def test_padrao_vem_do_segredo_ou_do_arquivo_local(tmp_path, monkeypatch):
    assert site.padrao_email_infra() is None
    monkeypatch.setenv("PADRAO_EMAIL_INFRA", "abc.def")
    assert site.padrao_email_infra().search(b"xx ABC-DEF")  # sem diferenciar maiúsculas
    monkeypatch.delenv("PADRAO_EMAIL_INFRA")
    arq = tmp_path / "padrao"
    arq.write_text("so-no-arquivo\n")
    monkeypatch.setattr(site, "ARQUIVO_PADRAO", arq)
    assert site.padrao_email_infra().search(b"... so-no-arquivo ...")


def test_no_workflow_o_padrao_e_obrigatorio(tmp_path, raiz):
    with pytest.raises(SiteInvalidoError, match="padrão do e-mail"):
        montar(_saida(tmp_path), raiz, None, exigir_padrao=True)
    assert not _saida(tmp_path).exists()
    montar(_saida(tmp_path), raiz, re.compile(rb"nada-disso-aparece"), exigir_padrao=True)


@pytest.mark.parametrize(
    "rel",
    [
        "index.html",
        "support.js",
        "src/ui/painel-logica.js",
        "src/ui/css/painel.css",
        "src/ui/vendor/inter/fonts.css",
    ],
)
@pytest.mark.parametrize(
    "endereco", [b"https://cdn.exemplo.test/x.js", b"http://exemplo.test/a.css"]
)
def test_arquivo_proprio_com_endereco_externo_e_recusado(tmp_path, raiz, rel, endereco):
    _editar(raiz, rel, lambda b: b + b"\n/* " + endereco + b" */")
    with pytest.raises(SiteInvalidoError, match="endereço externo"):
        montar(_saida(tmp_path), raiz)


def test_o_vendor_de_terceiros_pode_citar_enderecos_nos_comentarios(tmp_path):
    """react-dom cita links de documentação: o que vale é o index e o código próprio não dependerem de CDN."""
    react_dom = (RAIZ / "src/ui/vendor/react/react-dom.production.min.js").read_bytes()
    assert site.URL_EXTERNA.search(react_dom)
    montar(_saida(tmp_path))  # e a montagem real passa


# --- dados -------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel",
    [
        "src/ui/data/painel_dados.json",
        "src/ui/data/painel_indicadores.json",
        "src/ui/data/estado_fontes.json",
    ],
)
def test_json_quebrado_recusa_a_montagem(tmp_path, raiz, rel):
    (raiz / rel).write_text("{isto nao e json")
    with pytest.raises(SiteInvalidoError, match="JSON"):
        montar(_saida(tmp_path), raiz)


@pytest.mark.parametrize("chave", ["fontes", "estado", "municipios"])
def test_painel_dados_sem_bloco_essencial_e_recusado(tmp_path, raiz, chave):
    caminho = raiz / "src/ui/data/painel_dados.json"
    dados = json.loads(caminho.read_text("utf-8"))
    dados[chave] = {}
    caminho.write_text(json.dumps(dados))
    with pytest.raises(SiteInvalidoError, match="painel_dados"):
        montar(_saida(tmp_path), raiz)


def test_estado_das_fontes_fora_do_schema_e_recusado(tmp_path, raiz):
    caminho = raiz / "src/ui/data/estado_fontes.json"
    dados = json.loads(caminho.read_text("utf-8"))
    dados["fontes"]["TO-TER-01"]["status"] = "talvez"
    caminho.write_text(json.dumps(dados))
    with pytest.raises(SiteInvalidoError, match="estado_fontes"):
        montar(_saida(tmp_path), raiz)
    assert not _saida(tmp_path).exists()


# --- pasta de saída ----------------------------------------------------------------------------------


def test_saida_nao_pode_ser_o_projeto_nem_estar_dentro_dele_nem_conte_lo(tmp_path, raiz):
    for ruim in (raiz, raiz / "dentro", raiz.parent):
        with pytest.raises(SiteInvalidoError, match="projeto"):
            montar(ruim, raiz)
    assert (raiz / "index.html").exists() and not (raiz / "dentro").exists()


def test_pasta_com_outras_coisas_e_intocada(tmp_path):
    saida = _saida(tmp_path)
    saida.mkdir()
    (saida / "minhas-fotos.jpg").write_bytes(b"importante")
    with pytest.raises(SiteInvalidoError, match="não está vazia"):
        montar(saida)
    assert (saida / "minhas-fotos.jpg").read_bytes() == b"importante" and len(
        list(saida.iterdir())
    ) == 1


def test_saida_que_e_arquivo_e_recusada(tmp_path):
    arq = _saida(tmp_path)
    arq.write_text("x")
    with pytest.raises(SiteInvalidoError, match="não é uma pasta"):
        montar(arq)


def test_sincronizar_apaga_o_que_saiu_da_lista_e_preserva_o_git(tmp_path, raiz):
    saida = _saida(tmp_path)
    montar(saida, raiz)
    (saida / ".git").mkdir()
    (saida / ".git" / "config").write_text("[core]")
    (saida / "velho.html").write_text("saiu da lista")
    (saida / "bandeiras" / "extinta.webp").write_bytes(b"x")
    (saida / "pasta-velha").mkdir()
    (saida / "pasta-velha" / "a.js").write_text("x")
    r = montar(saida, raiz)
    assert r["removidos"] == 3
    tudo = _tudo(saida)
    assert (
        ".git/config" in tudo and "velho.html" not in tudo and "bandeiras/extinta.webp" not in tudo
    )
    assert not (saida / "pasta-velha").exists() and (saida / ".git").is_dir()


def test_clone_vazio_com_so_o_git_e_aceito(tmp_path, raiz):
    saida = _saida(tmp_path)
    (saida / ".git").mkdir(parents=True)
    montar(saida, raiz)
    assert (saida / "index.html").exists() and (saida / ".git").is_dir()


# --- linha de comando --------------------------------------------------------------------------------


def _cli():
    spec = importlib.util.spec_from_file_location(
        "montar_site", RAIZ / "scripts" / "montar_site.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_cli_monta_e_recusa_com_codigos_de_saida(tmp_path, capsys, monkeypatch):
    cli = _cli()
    assert cli.main(["--saida", str(_saida(tmp_path))]) == 0
    assert "escritos" in capsys.readouterr().out
    assert (
        cli.main(["--saida", str(_saida(tmp_path)), "--exigir-padrao"]) == 1
    )  # sem o padrão do e-mail
    assert "padrão do e-mail" in capsys.readouterr().err
    monkeypatch.setenv("PADRAO_EMAIL_INFRA", "nada-disso-aparece-no-site")
    assert cli.main(["--saida", str(_saida(tmp_path)), "--exigir-padrao"]) == 0


def test_cli_recusa_projeto_inteiro_como_saida(capsys):
    assert _cli().main(["--saida", str(RAIZ)]) == 1
    assert "Site recusado" in capsys.readouterr().err
