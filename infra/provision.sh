#!/usr/bin/env bash
# Datasets do BigQuery (task 31, modo Sandbox). Idempotente: só cria o que ainda não existe.
# Buckets, contas de serviço e orçamento (task 02) exigem faturamento e ficam fora deste script.
set -euo pipefail

PROJETO="${GCP_PROJECT:-project-6f15f3eb-e07f-48fc-ba7}"
LOCAL="southamerica-east1"  # região não muda depois de criada (decisão de 19/10)

for amb in dev hml ds; do
  for camada in raw stg mart; do
    ds="${amb}_${camada}"
    if bq --project_id="${PROJETO}" show "${PROJETO}:${ds}" >/dev/null 2>&1; then
      echo "já existe: ${ds}"
    else
      bq --project_id="${PROJETO}" mk --dataset --location="${LOCAL}" \
        --label=projeto:painel-to --label=ambiente:"${amb}" --label=modulo:"${camada}" \
        --description="Painel TO em Dados - ${amb}/${camada}" "${PROJETO}:${ds}"
    fi
  done
done
