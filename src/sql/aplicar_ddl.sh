#!/usr/bin/env bash
# Aplica os DDLs no BigQuery: bash src/sql/aplicar_ddl.sh <dev|hml|ds>   (task 31)
# Modo Sandbox (padrão, SANDBOX=1): sem DML e sem partição.
#   - executa só o CREATE de cada arquivo (corta no primeiro INSERT; os valores entram por
#     scripts/carregar_bigquery.py, que lê os STRUCT do próprio arquivo);
#   - fato_indicador sem PARTITION BY: no Sandbox a partição expira 60 dias após a SUA data,
#     o que apagaria todo período anterior (sondagem de 19/10, ver .planning/31).
# Idempotente: CREATE TABLE IF NOT EXISTS.
set -euo pipefail

AMBIENTE="${1:-dev}"
case "${AMBIENTE}" in dev|hml|ds) ;; *) echo "ambiente inválido: ${AMBIENTE} (use dev, hml ou ds)" >&2; exit 2 ;; esac
PROJETO="${GCP_PROJECT:-project-6f15f3eb-e07f-48fc-ba7}"
SANDBOX="${SANDBOX:-1}"
DDL_DIR="$(cd "$(dirname "$0")/ddl" && pwd)"
TABELAS=(dim_municipio dim_indicador dim_orgao dim_fonte dim_tempo dim_titular fato_indicador)

for t in "${TABELAS[@]}"; do
  # sem as linhas de comentário: o bq leria um "-- ..." inicial como opção de linha de comando
  sql="$(sed -n '/^INSERT INTO/q;p' "${DDL_DIR}/${t}.sql" | sed '/^[[:space:]]*--/d' \
    | sed -e "s/ds_mart\./${AMBIENTE}_mart./g" -e "s/(\"ambiente\", \"ds\")/(\"ambiente\", \"${AMBIENTE}\")/")"
  if [[ "${SANDBOX}" == "1" ]]; then sql="$(printf '%s\n' "${sql}" | sed '/^PARTITION BY/d')"; fi
  echo "-> ${AMBIENTE}_mart.${t}"
  bq --project_id="${PROJETO}" --location=southamerica-east1 query --nouse_legacy_sql --quiet \
    --maximum_bytes_billed=100000000 "${sql}" >/dev/null
done
echo "DDLs aplicados em ${AMBIENTE}_mart."
