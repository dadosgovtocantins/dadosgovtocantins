"""
Módulo Python de normalização do Código IBGE para 7 dígitos (RT-07).
"""


def fn_normaliza_codigo_ibge(cod: str | None) -> str | None:
    """
    Normaliza o código IBGE para 7 dígitos canônicos.
    Se possuir 6 dígitos (padrão TO 17XXXX), acrescenta o sufixo '0'.
    """
    if not cod:
        return None

    cod_limpo = str(cod).strip()
    if len(cod_limpo) == 6:
        return f"{cod_limpo}0"
    if len(cod_limpo) == 7:
        return cod_limpo

    return None
