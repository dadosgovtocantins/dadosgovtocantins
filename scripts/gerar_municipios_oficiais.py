"""
Script para baixar a lista oficial dos 139 municípios do Tocantins diretamente do IBGE
e atualizar src/ui/data/municipios_to.json.
"""

import json
import os

import requests

IBGE_MUNICIPIOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/17/municipios"
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src",
    "ui",
    "data",
    "municipios_to.json",
)


def atualizar_municipios_oficiais():
    print("🔄 Baixando lista oficial dos 139 municípios do Tocantins via API IBGE...")
    try:
        r = requests.get(IBGE_MUNICIPIOS_URL, timeout=15)
        r.raise_for_status()
        raw = r.json()

        # Ordena alfabeticamente ou mantendo id oficial IBGE
        lista_oficial = [
            {"id_municipio": str(m["id"]), "nome": m["nome"], "uf": "TO"}
            for m in sorted(raw, key=lambda x: x["nome"])
        ]

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(lista_oficial, f, ensure_ascii=False, indent=2)

        print(f"✅ Sucesso! {len(lista_oficial)} municípios oficiais salvos em: {OUT_PATH}")
        print("Primeiros 5 municípios:")
        for m in lista_oficial[:5]:
            print(f" - {m['nome']} (IBGE: {m['id_municipio']})")
    except Exception as e:
        print(f"❌ Erro ao baixar municípios do IBGE: {e}")


if __name__ == "__main__":
    atualizar_municipios_oficiais()
