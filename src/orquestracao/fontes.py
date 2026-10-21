"""Catálogo das 9 fontes que o painel já coleta e as regras de cadência de cada uma (Task 35).

Única definição usada pelo exportador, pelo estado e pelo orquestrador: acrescentar uma fonte nova
(tasks 39 a 45) começa aqui.
"""

# IBGE/SIDRA (7) e Tesouro/SICONFI (1): séries que viram indicadores no painel.
IMPLEMENTADOS = [
    "TO-TER-01",  # população residente
    "TO-TER-02",  # PIB municipal
    "TO-TER-03",  # PIB estadual
    "TO-TER-04",  # área territorial
    "TO-TER-05",  # produção agrícola municipal (PAM)
    "TO-TER-06",  # rebanho bovino (PPM)
    "TO-TER-07",  # taxa de desocupação (PNAD Contínua)
    "TO-REC-02",  # receita corrente líquida (SICONFI)
]
TITULARES = "TO-GER-01"  # TSE: titular eleito; dimensão própria, fora das séries de indicadores
FONTES = [*IMPLEMENTADOS, TITULARES]

TOTAL_MUNICIPIOS = 139

# Cadência de publicação da fonte. Mensal = a fonte é reverificada/recoletada todo mês (SICONFI e TSE).
PERIODICIDADE = {
    "TO-TER-01": "anual",
    "TO-TER-02": "anual",
    "TO-TER-03": "anual",
    "TO-TER-04": "anual",
    "TO-TER-05": "anual",
    "TO-TER-06": "anual",
    "TO-TER-07": "trimestral",
    "TO-REC-02": "mensal",
    "TO-GER-01": "mensal",
}

# Dias sem a fonte ser CONFIRMADA atual (coleta aceita, ou sentinela sem novidade) até virar "defasado":
# prazo da periodicidade + 50% (decisão do Bruno, 21/10/2026).
PRAZO_DEFASADO_DIAS = {"anual": 450, "trimestral": 150, "mensal": 60}

# Recoleta fixa, mesmo sem novidade na sentinela: o SICONFI recebe entregas tardias dos municípios e o
# TSE corrige cadastros (o zip é regravado). Só essas duas fontes.
RECOLETA_FIXA_DIAS = {"TO-REC-02": 30, "TO-GER-01": 30}
