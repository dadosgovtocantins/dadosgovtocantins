"""Monta a pasta do site público (Task 36): só o que está na lista fixa, conferido antes de qualquer cópia.

A lista é estrita: arquivo que ninguém colocou aqui NÃO vai para o repositório público, mesmo que esteja numa
pasta liberada (extensão fora da lista = erro, não omissão silenciosa). Antes de copiar, o conteúdo é varrido
atrás do e-mail da conta de infraestrutura e de segredos conhecidos, os dados são validados e os arquivos
próprios do painel não podem apontar para endereços externos.

A saída é sincronizada, não recriada: arquivo igual não é reescrito e arquivo que saiu da lista é apagado (a
pasta `.git` nunca é tocada), então a publicação incremental só muda o que mudou.
"""

import json
import os
import re
import shutil
from pathlib import Path

from src.orquestracao import estado as arquivo_estado

RAIZ = Path(__file__).resolve().parents[2]

ARQUIVOS = (
    "index.html",
    "support.js",
    "tocantins_municipios_regioes.geojson",
    "src/ui/painel-logica.js",
    "src/ui/css/painel.css",
    "src/ui/data/painel_dados.json",
    "src/ui/data/painel_indicadores.json",
    "src/ui/data/municipios_to.json",
    "src/ui/data/estado_fontes.json",
)
# Pasta -> extensões permitidas dentro dela (qualquer outra coisa é erro). Licenças entram pelo nome.
PASTAS = {
    "bandeiras": {".webp"},
    "src/ui/vendor": {".js", ".css", ".woff2"},
}
LICENCAS = {"LICENSE", "LICENSE.txt"}
IGNORADOS = {".DS_Store"}

# Arquivos PRÓPRIOS do painel: nada de endereço externo (CDN, fonte, analytics). O vendor é cópia de terceiros.
PROPRIOS = (
    "index.html",
    "support.js",
    "src/ui/painel-logica.js",
    "src/ui/css/painel.css",
    "src/ui/vendor/inter/fonts.css",
    "src/ui/vendor/phosphor/style.css",
)

GERADOS = {
    ".nojekyll": b"",
    "robots.txt": b"User-agent: *\nAllow: /\n",
    "404.html": (
        '<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Página não encontrada · Painel TO em Dados</title></head>"
        '<body style="font:16px/1.5 system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem">'
        '<h1>Página não encontrada</h1><p><a href="./">Voltar ao painel</a></p></body></html>\n'
    ).encode(),
}

SEGREDOS = {
    "chave privada": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "chave da AWS": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "token do GitHub": re.compile(
        rb"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{40,}"
    ),
    "chave de API do Google": re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"),
    "conta de infraestrutura": re.compile(rb"dadosgovtocantins@", re.IGNORECASE),
}
URL_EXTERNA = re.compile(rb"https?://[^\s\"')<>]+", re.IGNORECASE)
ARQUIVO_PADRAO = Path.home() / ".config" / "painel-to" / "padrao-email-infra"


class SiteInvalidoError(ValueError):
    """A montagem foi recusada: nada foi copiado."""


def padrao_email_infra() -> re.Pattern[bytes] | None:
    """Padrão (regex) do e-mail de infraestrutura: segredo do GitHub (PADRAO_EMAIL_INFRA) ou arquivo local."""
    texto = os.environ.get("PADRAO_EMAIL_INFRA", "").strip()
    if not texto and ARQUIVO_PADRAO.is_file():
        texto = ARQUIVO_PADRAO.read_text("utf-8").strip()
    return re.compile(texto.encode(), re.IGNORECASE) if texto else None


def listar(raiz: Path = RAIZ) -> dict[str, Path]:
    """Caminho relativo (com /) -> arquivo de origem, em ordem fixa. Erro se faltar arquivo ou sobrar um intruso."""
    achados: dict[str, Path] = {}
    for rel in ARQUIVOS:
        origem = raiz / rel
        if not origem.is_file():
            raise SiteInvalidoError(f"arquivo da lista do site não existe: {rel}")
        achados[rel] = origem
    for pasta, extensoes in PASTAS.items():
        base = raiz / pasta
        if not base.is_dir():
            raise SiteInvalidoError(f"pasta da lista do site não existe: {pasta}")
        for origem in sorted(p for p in base.rglob("*") if p.is_file()):
            if origem.name in IGNORADOS:
                continue
            rel = origem.relative_to(raiz).as_posix()
            if origem.suffix.lower() not in extensoes and origem.name not in LICENCAS:
                raise SiteInvalidoError(f"arquivo fora da lista em pasta liberada: {rel}")
            achados[rel] = origem
    return dict(sorted(achados.items()))


def _validar_dados(conteudos: dict[str, bytes]) -> None:
    for rel in (r for r in conteudos if r.startswith("src/ui/data/") or r.endswith(".geojson")):
        try:
            json.loads(conteudos[rel])
        except ValueError as erro:
            raise SiteInvalidoError(f"{rel} não é JSON válido") from erro
    pd = json.loads(conteudos["src/ui/data/painel_dados.json"])
    if not all(isinstance(pd.get(k), dict) and pd[k] for k in ("fontes", "estado", "municipios")):
        raise SiteInvalidoError("painel_dados.json sem fontes, estado ou municípios")
    try:
        arquivo_estado.validar(json.loads(conteudos["src/ui/data/estado_fontes.json"]))
    except arquivo_estado.EstadoInvalidoError as erro:
        raise SiteInvalidoError(f"estado_fontes.json inválido: {erro}") from erro


def conferir(conteudos: dict[str, bytes], padrao: re.Pattern[bytes] | None) -> None:
    """Levanta SiteInvalidoError citando só NOMES de arquivo e o tipo do achado, nunca o conteúdo."""
    problemas = []
    for rel, dados in conteudos.items():
        for nome, rx in SEGREDOS.items():
            if rx.search(dados):
                problemas.append(f"{rel}: {nome}")
        if padrao is not None and padrao.search(dados):
            problemas.append(f"{rel}: padrão do e-mail de infraestrutura")
    for rel in PROPRIOS:
        if rel in conteudos and URL_EXTERNA.search(conteudos[rel]):
            problemas.append(f"{rel}: endereço externo (o site não depende de terceiros)")
    if problemas:
        raise SiteInvalidoError("conteúdo recusado: " + "; ".join(problemas))
    _validar_dados(conteudos)


def montar(
    saida: Path,
    raiz: Path = RAIZ,
    padrao: re.Pattern[bytes] | None = None,
    exigir_padrao: bool = False,
) -> dict[str, int]:
    """Sincroniza `saida` com o site. Devolve {"escritos", "iguais", "removidos"}."""
    raiz, saida = Path(raiz).resolve(), Path(saida).resolve()
    if saida == raiz or saida in raiz.parents or raiz in saida.parents:
        raise SiteInvalidoError("a pasta de saída não pode conter nem ficar dentro do projeto")
    if exigir_padrao and padrao is None:
        raise SiteInvalidoError(
            "padrão do e-mail de infraestrutura indisponível (PADRAO_EMAIL_INFRA)"
        )

    origens = listar(raiz)
    conteudos = {rel: p.read_bytes() for rel, p in origens.items()} | dict(GERADOS)
    conferir(conteudos, padrao)

    if saida.exists() and not saida.is_dir():
        raise SiteInvalidoError(f"{saida} existe e não é uma pasta")
    if (
        saida.is_dir()
        and any(saida.iterdir())
        and not ((saida / ".git").exists() or (saida / ".nojekyll").exists())
    ):
        raise SiteInvalidoError("a pasta de saída não está vazia e não parece um site já montado")
    saida.mkdir(parents=True, exist_ok=True)

    escritos = iguais = 0
    for rel, dados in sorted(conteudos.items()):
        destino = saida / rel
        if destino.is_file() and destino.read_bytes() == dados:
            iguais += 1
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(dados)
        escritos += 1

    removidos = 0
    for existente in sorted((p for p in saida.rglob("*") if p.is_file()), reverse=True):
        rel = existente.relative_to(saida)
        if rel.parts[0] == ".git" or rel.as_posix() in conteudos:
            continue
        existente.unlink()
        removidos += 1
    for pasta in sorted(
        (p for p in saida.rglob("*") if p.is_dir() and p.name != ".git"), reverse=True
    ):
        if ".git" not in pasta.relative_to(saida).parts and not any(pasta.iterdir()):
            shutil.rmtree(pasta)
    return {"escritos": escritos, "iguais": iguais, "removidos": removidos}
