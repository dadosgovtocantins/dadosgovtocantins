"""
Script para popular src/sql/ddl/dim_municipio.sql com todos os 139 municípios oficiais do Tocantins.
"""

import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT_DIR, "src", "ui", "data", "municipios_to.json")
SQL_PATH = os.path.join(ROOT_DIR, "src", "sql", "ddl", "dim_municipio.sql")


def gerar_ddl_dim_municipio():
    with open(JSON_PATH, encoding="utf-8") as f:
        municipios = json.load(f)

    sql_lines = [
        "-- DDL da Dimensão Município: dim_municipio",
        "-- Chave canônica = Código IBGE de 7 dígitos (RT-07) - Exatamente 139 municípios do TO",
        "",
        "CREATE TABLE IF NOT EXISTS `ds_mart.dim_municipio` (",
        '  id_municipio     STRING    NOT NULL OPTIONS(description="Código IBGE de 7 dígitos (ex: 1721000)"),',
        '  nome_municipio   STRING    NOT NULL OPTIONS(description="Nome oficial do município sem acentuação/normalizado"),',
        '  nome_exibicao    STRING    NOT NULL OPTIONS(description="Nome formatado para exibição visual"),',
        "  uf               STRING    NOT NULL OPTIONS(description=\"UF (sempre 'TO')\"),",
        '  microrregiao     STRING             OPTIONS(description="Microrregião IBGE"),',
        '  mesorregiao      STRING             OPTIONS(description="Mesorregião IBGE"),',
        '  latitude         FLOAT64            OPTIONS(description="Latitude da sede municipal"),',
        '  longitude        FLOAT64            OPTIONS(description="Longitude da sede municipal")',
        ");",
        "",
        "-- Povoamento canônico dos 139 municípios do Tocantins com código IBGE oficial de 7 dígitos",
        "INSERT INTO `ds_mart.dim_municipio` (id_municipio, nome_municipio, nome_exibicao, uf)",
        "SELECT * FROM UNNEST([",
    ]

    structs = []
    for m in municipios:
        nome_norm = (
            m["nome"]
            .upper()
            .replace("Á", "A")
            .replace("Ã", "A")
            .replace("Â", "A")
            .replace("É", "E")
            .replace("Ê", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ô", "O")
            .replace("Ú", "U")
            .replace("Ç", "C")
        )
        structs.append(
            f"  STRUCT('{m['id_municipio']}' AS id_municipio, '{nome_norm}' AS nome_municipio, '{m['nome']}' AS nome_exibicao, 'TO' AS uf)"
        )

    sql_lines.append(",\n".join(structs))
    sql_lines.append("]);")
    sql_lines.append("")

    with open(SQL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print(
        f"✅ SQL dim_municipio.sql atualizado com os {len(municipios)} municípios oficiais em: {SQL_PATH}"
    )


if __name__ == "__main__":
    gerar_ddl_dim_municipio()
