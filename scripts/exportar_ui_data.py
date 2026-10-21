"""
Script para converter os dados coletados das APIs reais em JSON consumível pela UI.
"""

import json
import os

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
UI_DATA_DIR = os.path.join(ROOT_DIR, "src", "ui", "data")


def atualizar_dados_ui():
    os.makedirs(UI_DATA_DIR, exist_ok=True)

    path_ibge = os.path.join(DATA_DIR, "ibge_populacao_to.csv")
    path_siconfi = os.path.join(DATA_DIR, "siconfi_execucao_to.csv")

    coletados = {
        "ibge_populacao": [],
        "siconfi_execucao": [],
        "dt_atualizacao": pd.Timestamp.now().isoformat(),
    }

    if os.path.exists(path_ibge):
        df_ibge = pd.read_csv(path_ibge)
        coletados["ibge_populacao"] = df_ibge.to_dict(orient="records")
        print(f"✅ IBGE: {len(df_ibge)} registros convertidos para UI.")

    if os.path.exists(path_siconfi):
        df_siconfi = pd.read_csv(path_siconfi)
        coletados["siconfi_execucao"] = df_siconfi.to_dict(orient="records")
        print(f"✅ SICONFI: {len(df_siconfi)} registros convertidos para UI.")

    path_out = os.path.join(UI_DATA_DIR, "dados_coletados_real.json")
    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(coletados, f, ensure_ascii=False, indent=2)

    print(f"💾 UI Data atualizada em: {path_out}")


if __name__ == "__main__":
    atualizar_dados_ui()
