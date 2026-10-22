#!/usr/bin/env bash
# Publica o site no repositório público de forma INCREMENTAL (Task 36).
#   bash scripts/publicar_site.sh <url-do-repositorio-publico> [ramo=main]
#
# Clona o repositório público (raso), sincroniza a pasta com scripts/montar_site.py (só mudam os arquivos que
# mudaram: bandeiras e GeoJSON não são regravados) e commita SÓ SE houver diferença. Nunca usa --force.
# A autenticação é uma DEPLOY KEY SSH (chave que vale para UM repositório, com escrita): PAINEL_DEPLOY_KEY traz a
# chave privada, que vai para um arquivo temporário 0600 apagado ao sair, e nada aqui imprime variáveis nem liga o
# modo de depuração do shell. O servidor é conferido contra as chaves oficiais da GitHub em scripts/github_known_hosts
# (StrictHostKeyChecking=yes), sem configuração nem agente SSH da máquina.
# Variáveis: PAINEL_DEPLOY_KEY (chave privada, só para URL ssh), PYTHON (padrão: python3), PADRAO_EMAIL_INFRA (obrigatório).
set -euo pipefail
set +x

URL="${1:?uso: publicar_site.sh <url-do-repositorio-publico> [ramo]}"
RAMO="${2:-main}"
PYTHON="${PYTHON:-python3}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export GIT_TERMINAL_PROMPT=0

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

if [[ -n "${PAINEL_DEPLOY_KEY:-}" ]]; then
  CHAVE="${TMP}/deploy_key"
  (umask 077 && printf '%s\n' "${PAINEL_DEPLOY_KEY}" > "${CHAVE}")
  export GIT_SSH_COMMAND="ssh -F /dev/null -i '${CHAVE}' -o IdentitiesOnly=yes -o IdentityAgent=none -o BatchMode=yes -o UserKnownHostsFile='${RAIZ}/scripts/github_known_hosts' -o StrictHostKeyChecking=yes"
fi

CLONE="${TMP}/painel"

git clone --quiet --depth 1 "${URL}" "${CLONE}" || { echo "ERRO: não consegui clonar o repositório público." >&2; exit 1; }
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

# Nenhum erro é escondido: sucesso só é declarado depois de conferir, NO REMOTO, que o ramo aponta para o commit.
if ! git push --quiet origin "HEAD:${RAMO}"; then
  if git ls-remote --exit-code --heads origin "${RAMO}" >/dev/null 2>&1; then
    echo "Push recusado; o ramo existe no remoto, atualizando e tentando uma vez mais." >&2
    git pull --quiet --rebase origin "${RAMO}" || { echo "ERRO: não consegui atualizar o clone." >&2; exit 1; }
    git push --quiet origin "HEAD:${RAMO}" || { echo "ERRO: o push foi recusado de novo; nada foi publicado." >&2; exit 1; }
  else
    echo "ERRO: o push foi recusado (a deploy key precisa ter escrita no repositório público); nada foi publicado." >&2
    exit 1
  fi
fi
remoto="$(git ls-remote origin "refs/heads/${RAMO}" | cut -f1)"
if [[ -z "${remoto}" || "${remoto}" != "$(git rev-parse HEAD)" ]]; then
  echo "ERRO: depois do push o remoto não aponta para o commit publicado; nada foi publicado." >&2
  exit 1
fi
echo "Site publicado: $(git rev-parse --short HEAD)."
