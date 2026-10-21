#!/usr/bin/env bash
# Publica o site no repositório público de forma INCREMENTAL (Task 36).
#   bash scripts/publicar_site.sh <url-do-repositorio-publico> [ramo=main]
#
# Clona o repositório público (raso), sincroniza a pasta com scripts/montar_site.py (só mudam os arquivos que
# mudaram: bandeiras e GeoJSON não são regravados) e commita SÓ SE houver diferença. Nunca usa --force.
# O token (PAT_PUBLICACAO_PAINEL, só para https) vai por variável de ambiente do Git, nunca na URL nem no
# argumento de um comando, e nada aqui imprime variáveis nem liga o modo de depuração do shell.
# Variáveis: PAT_PUBLICACAO_PAINEL (token), PYTHON (padrão: python3), PADRAO_EMAIL_INFRA (obrigatório).
set -euo pipefail
set +x

URL="${1:?uso: publicar_site.sh <url-do-repositorio-publico> [ramo]}"
RAMO="${2:-main}"
PYTHON="${PYTHON:-python3}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${PAT_PUBLICACAO_PAINEL:-}" && "${URL}" == https://github.com/* ]]; then
  cabecalho="$(printf 'x-access-token:%s' "${PAT_PUBLICACAO_PAINEL}" | base64 | tr -d '\n')"
  export GIT_CONFIG_COUNT=1
  export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
  export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic ${cabecalho}"
fi
export GIT_TERMINAL_PROMPT=0

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT
CLONE="${TMP}/painel"

git clone --quiet --depth 1 "${URL}" "${CLONE}" 2>/dev/null || { echo "ERRO: não consegui clonar o repositório público." >&2; exit 1; }
git -C "${CLONE}" checkout --quiet -B "${RAMO}"

"${PYTHON}" "${RAIZ}/scripts/montar_site.py" --saida "${CLONE}" --exigir-padrao

cd "${CLONE}"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
if git diff --cached --quiet; then
  echo "Nada a publicar: o site público já está igual."
  exit 0
fi
git commit --quiet -m "site: atualização do painel ($(git diff --cached --name-only | wc -l | tr -d ' ') arquivo(s))"
git push --quiet origin "HEAD:${RAMO}" 2>/dev/null || {
  git pull --quiet --rebase origin "${RAMO}" && git push --quiet origin "HEAD:${RAMO}"
}
echo "Site publicado: $(git rev-parse --short HEAD)."
