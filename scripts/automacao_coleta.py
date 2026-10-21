"""
Script de Automação Contínua de Coleta de Dados Públicos do Tocantins (PIBIEX/Unitins).
Coleta automática de APIs oficiais (IBGE SIDRA, STN/SICONFI, MTE CAGED, DATASUS).
"""

import os
import sys
from datetime import UTC, datetime

import pandas as pd
import requests

# APIs Oficiais Abertas
SICONFI_API_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324?localidades=N6[N3[17]]"
CAGED_API_URL = "https://pdet.mte.gov.br/images/Novo_CAGED/2024"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def coletar_dados_ibge_to():
    """Extrai a população residente dos 139 municípios do TO via API SIDRA/IBGE."""
    print(f"[{datetime.now().isoformat()}] 🔄 Coletando IBGE SIDRA (População TO)...")
    try:
        response = requests.get(IBGE_API_URL, timeout=30)
        response.raise_for_status()
        dados = response.json()
        resultados = []
        if dados and len(dados) > 0:
            for item in dados[0]["resultados"][0]["series"]:
                cod_ibge = item["localidade"]["id"]
                nome_mun = item["localidade"]["nome"]
                populacao = next(iter(item["serie"].values()))
                resultados.append(
                    {
                        "id_municipio": cod_ibge,
                        "municipio": nome_mun,
                        "populacao_estimada": int(populacao) if str(populacao).isdigit() else None,
                        "fonte": "IBGE-SIDRA-TO-TER-01",
                        "dt_coleta": datetime.now(UTC).isoformat(),
                    }
                )
        print(f"✅ IBGE: {len(resultados)} municípios atualizados.")
        return resultados
    except Exception as e:
        # Nunca substitui por dado simulado (RF-55): o CSV anterior é mantido.
        print(f"❌ Erro ao coletar IBGE: {e}")
        return None


def coletar_dados_siconfi_to(ano=2023):
    """Extrai os dados fiscais e receita corrente líquida do TO via API SICONFI/STN."""
    print(f"[{datetime.now().isoformat()}] 🔄 Coletando SICONFI/STN (Receitas e LRF TO)...")
    params = {"an_exercicio": ano, "id_ente": 17, "no_anexo": "DCA-Anexo I-C"}
    try:
        response = requests.get(SICONFI_API_URL, params=params, timeout=30)
        response.raise_for_status()
        dados = response.json()
        items = dados.get("items", [])
        print(f"✅ SICONFI: {len(items)} registros Fiscais coletados.")
        return items
    except Exception as e:
        # Nunca substitui por dado simulado (RF-55): o CSV anterior é mantido.
        print(f"❌ Erro ao coletar SICONFI: {e}")
        return None


def executar_pipeline_completo():
    """Executa a extração, transforma em DataFrame e salva em CSV e JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    print("\n" + "=" * 60)
    print("🚀 EXECUTANDO PIPELINE AUTOMÁTICO DE COLETA DE DADOS TO")
    print("=" * 60)

    falhas = []

    # 1. Coleta IBGE
    ibge_data = coletar_dados_ibge_to()
    if not ibge_data:
        falhas.append("IBGE")
    else:
        df_ibge = pd.DataFrame(ibge_data)
        path_csv = os.path.join(DATA_DIR, "ibge_populacao_to.csv")
        df_ibge.to_csv(path_csv, index=False, encoding="utf-8-sig")
        print(f"💾 IBGE salvo em: {path_csv}")

    # 2. Coleta SICONFI
    siconfi_data = coletar_dados_siconfi_to()
    if not siconfi_data:
        falhas.append("SICONFI")
    else:
        df_siconfi = pd.DataFrame(siconfi_data)
        path_csv = os.path.join(DATA_DIR, "siconfi_execucao_to.csv")
        df_siconfi.to_csv(path_csv, index=False, encoding="utf-8-sig")
        print(f"💾 SICONFI salvo em: {path_csv}")

    if falhas:
        print(
            f"\n❌ PIPELINE COM FALHA ({', '.join(falhas)}). Os dados anteriores foram mantidos em {DATA_DIR}."
        )
        sys.exit(1)
    print("\n✅ PIPELINE CONCLUÍDO COM SUCESSO! Dados atualizados em " + DATA_DIR)


if __name__ == "__main__":
    executar_pipeline_completo()
