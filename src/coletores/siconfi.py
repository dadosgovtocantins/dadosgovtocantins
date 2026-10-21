"""Leitura da Receita Corrente Líquida (RCL) no SICONFI/Tesouro Nacional (Task 28).

Fonte principal: RREO Anexo 3 (RCL dos últimos 12 meses, 6º bimestre). Municípios com menos de 50 mil habitantes
podem entregar o RREO Simplificado, que não tem o Anexo 3; para eles a mesma RCL está no RGF Anexo 1.
"""

import json
from datetime import UTC, datetime
from typing import Any

from src.coletor_base.excecoes import ValidacaoError
from src.coletor_base.http import ClienteHTTP

URL_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/17/municipios"
URL_RREO = (
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={ano}&nr_periodo=6"
    "&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2003&id_ente={ente}"
)
URL_EXTRATO = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/extrato_entregas?id_ente={ente}&an_referencia={ano}"
URL_RGF = (
    "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf?an_exercicio={ano}&in_periodicidade={periodicidade}"
    "&nr_periodo={periodo}&co_tipo_demonstrativo={demonstrativo}&co_poder=E&no_anexo=RGF-Anexo%2001&id_ente={ente}"
)
# A API do Tesouro bloqueia (429) quem consulta demais: 1 s entre consultas e até 5 tentativas com espera crescente.
ATRASO_ENTRE_CONSULTAS_S, MAX_TENTATIVAS = 1.0, 5
CONTA_RREO, COLUNA_RREO = "RREO3ReceitaCorrenteLiquida", "TOTAL (ÚLTIMOS 12 MESES)"
CONTA_RGF, COLUNA_RGF = "ReceitaCorrenteLiquidaLimiteLegal", "Valor"
# (periodicidade, período, demonstrativo): semestral simplificado primeiro (é o caso dos municípios pequenos).
RGF_ALTERNATIVAS = [("S", 2, "RGF%20Simplificado"), ("Q", 3, "RGF")]


def exercicios_alvo(ano_atual: int, quantidade: int = 3) -> range:
    """Exercícios fechados que o coletor lê: o ano passado e os anteriores (a sentinela olha os mesmos)."""
    ultimo = ano_atual - 1
    return range(ultimo - quantidade + 1, ultimo + 1)


def _rcl(
    http: ClienteHTTP, url: str, conta: str, coluna: str, descricao: str
) -> list[dict[str, Any]]:
    resp = json.loads(http.get(url))
    if resp.get("hasMore"):
        raise ValidacaoError(f"SICONFI paginou a resposta de {descricao}.")
    return [i for i in resp["items"] if i["cod_conta"] == conta and i["coluna"] == coluna]


def coletar_rcl(exercicios: int = 3) -> bytes:
    """Baixa a RCL anual do estado e dos 139 municípios nos últimos exercícios fechados.

    A zona raw guarda só a linha da RCL de cada ente (a resposta completa tem ~100 KB por ente)
    e a origem do valor ("RREO" ou "RGF"); ente sem nenhum dos dois não gera item (RF-55).
    """
    http = ClienteHTTP(
        delay_segundos=ATRASO_ENTRE_CONSULTAS_S, max_retries=MAX_TENTATIVAS, backoff_factor=2.0
    )
    entes = ["17", *(str(m["id"]) for m in json.loads(http.get(URL_MUNICIPIOS)))]
    itens = []
    for ano in exercicios_alvo(datetime.now(UTC).year, exercicios):
        for ente in entes:
            achados = _rcl(
                http, URL_RREO.format(ano=ano, ente=ente), CONTA_RREO, COLUNA_RREO, f"{ente}/{ano}"
            )
            origem = "RREO"
            for periodicidade, periodo, demonstrativo in RGF_ALTERNATIVAS:
                if achados:
                    break
                url = URL_RGF.format(
                    ano=ano,
                    ente=ente,
                    periodicidade=periodicidade,
                    periodo=periodo,
                    demonstrativo=demonstrativo,
                )
                achados, origem = (
                    _rcl(http, url, CONTA_RGF, COLUNA_RGF, f"{ente}/{ano} (RGF)"),
                    "RGF",
                )
            itens += [
                {
                    "cod_ibge": i["cod_ibge"],
                    "exercicio": i["exercicio"],
                    "valor": i["valor"],
                    "origem": origem,
                }
                for i in achados
            ]
    return json.dumps({"itens": itens}).encode("utf-8")


def ler_itens(bruto: bytes) -> list[dict[str, Any]]:
    """Valida e devolve os itens (cod_ibge, exercicio, valor em R$) gravados por coletar_rcl()."""
    try:
        itens = json.loads(bruto.decode("utf-8"))["itens"]
        return [
            {
                "cod_ibge": str(i["cod_ibge"]),
                "exercicio": int(i["exercicio"]),
                "valor": float(i["valor"]),
            }
            for i in itens
        ]
    except (ValueError, KeyError, TypeError) as e:
        raise ValidacaoError(f"Payload SICONFI em formato inesperado: {e!r}") from e
