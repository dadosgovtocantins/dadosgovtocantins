#!/usr/bin/env bash
# Varredura de segredos no HISTÓRICO INTEIRO e na árvore (Task 34).
#   bash scripts/varrer_segredos.sh          (da raiz do repositório ou de qualquer subpasta)
#
# 1) Padrão do e-mail da conta de infraestrutura (PADRAO_EMAIL_INFRA, ou o arquivo local
#    ~/.config/painel-to/padrao-email-infra): metadados e diffs de TODOS os commits, árvore atual,
#    arquivos novos ainda não commitados e conteúdo de arquivos compactados (.pptx, .zip...).
# 2) gitleaks em todos os commits (GITLEAKS_BIN ou o do PATH), com valores ocultos (--redact).
#
# Só imprime contagens e NOMES de arquivo/commit: nunca o conteúdo nem o padrão.
# Sai com 0 se tudo limpo, 1 se achou algo ou se faltou o gitleaks, 2 se faltou o padrão.
# Compatível com o bash 3.2 do macOS (sem arrays, sem mapfile).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PADRAO="${PADRAO_EMAIL_INFRA:-}"
if [[ -z "${PADRAO}" && -r "${HOME}/.config/painel-to/padrao-email-infra" ]]; then
  PADRAO="$(cat "${HOME}/.config/painel-to/padrao-email-infra")"
fi
if [[ -z "${PADRAO}" ]]; then
  echo "ERRO: defina PADRAO_EMAIL_INFRA (ou crie ~/.config/painel-to/padrao-email-infra)." >&2
  exit 2
fi

falhas=0
achado() { echo "ACHADO: $1" >&2; falhas=$((falhas + 1)); }

echo "== 1. padrão do e-mail de infraestrutura"

# 1a) autor, committer e mensagem de todos os commits
n="$(git log --all --format='%an %ae %cn %ce%n%B' 2>/dev/null | grep -c -i -E -e "${PADRAO}" || true)"
if [[ "${n}" != "0" ]]; then achado "metadados de commit (autor, committer ou mensagem): ${n} linha(s)"; else echo "ok: metadados dos commits"; fi

# 1b) linhas adicionadas ou removidas em qualquer commit de qualquer ramo
n="$(git log --all --format='%h' -i -E -G "${PADRAO}" 2>/dev/null | wc -l | tr -d ' ')"
if [[ "${n}" != "0" ]]; then achado "${n} commit(s) do histórico contêm o padrão em diffs: $(git log --all --format='%h' -i -E -G "${PADRAO}" | tr '\n' ' ')"; else echo "ok: diffs de todos os commits"; fi

# 1c) árvore rastreada e arquivos novos ainda não commitados (respeita o .gitignore)
# (git grep sai com 1 quando não acha nada: com pipefail isso derrubaria o script, daí o "|| true")
nomes="$(git grep -I -i -l -E --untracked -e "${PADRAO}" 2>/dev/null || true)"
if [[ -n "${nomes}" ]]; then achado "$(printf '%s\n' "${nomes}" | wc -l | tr -d ' ') arquivo(s) contêm o padrão: $(printf '%s' "${nomes}" | tr '\n' ' ')"; else echo "ok: arquivos de texto"; fi

# 1d) dentro de arquivos compactados (.pptx é um zip: o grep direto não enxerga o conteúdo)
comp=0
while IFS= read -r -d '' f; do
  comp=$((comp + 1))
  m="$(unzip -p "${f}" 2>/dev/null | grep -a -c -i -E -e "${PADRAO}" || true)"
  if [[ "${m}" != "0" ]]; then achado "arquivo compactado contém o padrão: ${f}"; fi
done < <(git ls-files -z --cached --others --exclude-standard -- '*.pptx' '*.docx' '*.xlsx' '*.odt' '*.ods' '*.zip' '*.jar')
echo "ok: ${comp} arquivo(s) compactado(s) conferido(s)"

echo "== 2. gitleaks (histórico inteiro)"
GL="${GITLEAKS_BIN:-$(command -v gitleaks || true)}"
if [[ -z "${GL}" ]]; then
  achado "gitleaks não encontrado (instale ou defina GITLEAKS_BIN)"
elif "${GL}" git --help >/dev/null 2>&1; then
  if "${GL}" git --redact --no-banner --log-opts="--all" .; then echo "ok: gitleaks"; else achado "gitleaks encontrou segredo (valores ocultos)"; fi
else
  if "${GL}" detect --redact --no-banner --source . --log-opts="--all"; then echo "ok: gitleaks"; else achado "gitleaks encontrou segredo (valores ocultos)"; fi
fi

if [[ "${falhas}" -ne 0 ]]; then
  echo "REPROVADO: ${falhas} problema(s)." >&2
  exit 1
fi
echo "APROVADO: nenhum achado."
