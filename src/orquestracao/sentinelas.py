"""Sentinelas: a consulta barata e oficial que diz se uma fonte tem dado novo (Task 35, passo 4).

Cada sentinela devolve uma `marca` (texto opaco): se for diferente da guardada em estado_fontes.json, há
novidade e a fonte inteira é coletada. Nenhuma sentinela baixa dado de verdade (nem o zip de 64 MB do TSE).

  IBGE    /agregados/{id}/periodos  -> "último período|data de modificação" (revisão também conta)
  SICONFI extrato_entregas do estado -> "última entrega de RREO(6º bimestre)/RGF|quantas entregas"
  TSE     data de hoje               -> eleição vigente de cada cargo (o zip é regravado todo dia: não serve)
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, ClassVar

import urllib3

from src.coletores import siconfi
from src.coletores.sidra import URL_BASE as URL_SIDRA
from src.coletores.tse_candidatos import eleicoes_vigentes, proxima_posse

URL_CALENDARIO = "https://servicodados.ibge.gov.br/api/v3/calendario/?de={de}&ate={ate}&qtd=300"
ENTE_ESTADO = 17
JANELA_CALENDARIO_DIAS = 400
FALHAS_DE_REDE = (
    OSError,
    urllib3.exceptions.HTTPError,
    ValueError,
    KeyError,
    TypeError,
    AttributeError,
)


class SentinelaError(RuntimeError):
    """A sentinela não conseguiu verificar a fonte (rede, formato inesperado, fonte desconhecida)."""


@dataclass(frozen=True)
class Sentinela:
    marca: str
    ultimo_periodo: str | None = None
    proxima_divulgacao: str | None = None  # AAAA-MM-DD, quando a fonte anuncia
    aviso: str | None = None  # algo secundário falhou (ex.: calendário), sem invalidar a marca


class Sentinelas:
    """Consulta a sentinela de cada fonte. `get` é o GET do ClienteHTTP (ou um falso nos testes)."""

    # Agregado SIDRA de cada coletor do IBGE (um teste confere com os coletores).
    AGREGADOS: ClassVar[dict[str, str]] = {
        "TO-TER-01": "6579",
        "TO-TER-02": "5938",
        "TO-TER-03": "5938",
        "TO-TER-04": "4714",
        "TO-TER-05": "5457",
        "TO-TER-06": "3939",
        "TO-TER-07": "4099",
    }
    # Produto do calendário do IBGE, só onde conhecido (PNAD Contínua trimestral); os demais ficam sem data.
    PRODUTO_CALENDARIO: ClassVar[dict[str, int]] = {"TO-TER-07": 9173}

    def __init__(self, get: Callable[[str], bytes], hoje: date):
        self._get, self._hoje = get, hoje
        self._periodos: dict[
            str, list[dict[str, str]]
        ] = {}  # TER-02 e TER-03 dividem o agregado 5938

    def consultar(self, id_fonte: str) -> Sentinela:
        try:
            if id_fonte in self.AGREGADOS:
                return self._ibge(id_fonte)
            if id_fonte == "TO-REC-02":
                return self._siconfi()
            if id_fonte == "TO-GER-01":
                return self._tse()
        except FALHAS_DE_REDE as erro:
            raise SentinelaError(
                f"{id_fonte}: sentinela falhou: {type(erro).__name__}: {erro}"[:300]
            ) from erro
        raise SentinelaError(f"{id_fonte}: fonte desconhecida")

    # --- IBGE --------------------------------------------------------------------------------------

    def _lista_de_periodos(self, agregado: str) -> list[dict[str, str]]:
        if agregado not in self._periodos:
            lista = json.loads(self._get(f"{URL_SIDRA}/{agregado}/periodos"))
            if not isinstance(lista, list) or not lista:
                raise ValueError(f"lista de períodos vazia ou inesperada no agregado {agregado}")
            for item in lista:
                if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                    raise ValueError(f"período sem id no agregado {agregado}: {item!r}")
                datetime.strptime(
                    item["modificacao"], "%d/%m/%Y"
                )  # KeyError/ValueError se faltar ou for inválida
            self._periodos[agregado] = lista
        return self._periodos[agregado]

    def _ibge(self, id_fonte: str) -> Sentinela:
        ultimo = max(self._lista_de_periodos(self.AGREGADOS[id_fonte]), key=lambda p: str(p["id"]))
        modificacao = datetime.strptime(ultimo["modificacao"], "%d/%m/%Y").date().isoformat()
        proxima, aviso = self._proxima_divulgacao_ibge(id_fonte)
        return Sentinela(f"{ultimo['id']}|{modificacao}", str(ultimo["id"]), proxima, aviso)

    def _proxima_divulgacao_ibge(self, id_fonte: str) -> tuple[str | None, str | None]:
        produto = self.PRODUTO_CALENDARIO.get(id_fonte)
        if produto is None:
            return None, None
        url = URL_CALENDARIO.format(
            de=self._hoje.strftime("%m-%d-%Y"),
            ate=(self._hoje + timedelta(days=JANELA_CALENDARIO_DIAS)).strftime("%m-%d-%Y"),
        )
        try:
            itens: list[Any] = json.loads(self._get(url))["items"]
            datas = [
                d
                for i in itens
                if i["produto_id"] == produto
                and (d := datetime.strptime(i["data_divulgacao"][:10], "%d/%m/%Y").date())
                >= self._hoje
            ]
        except FALHAS_DE_REDE as erro:
            return None, f"calendário do IBGE indisponível: {type(erro).__name__}"
        return (min(datas).isoformat() if datas else None), None

    # --- SICONFI -----------------------------------------------------------------------------------

    def _siconfi(self) -> Sentinela:
        datas, anos_com_rreo = [], []
        for ano in siconfi.exercicios_alvo(self._hoje.year):
            resposta = json.loads(self._get(siconfi.URL_EXTRATO.format(ente=ENTE_ESTADO, ano=ano)))
            if resposta.get("hasMore"):
                raise ValueError(
                    "o SICONFI paginou o extrato de entregas; a sentinela não enxerga tudo"
                )
            for item in resposta["items"]:
                rreo_anual = (
                    item["entregavel"].startswith("Relatório Resumido") and item["periodo"] == 6
                )
                if not (rreo_anual or item["entregavel"].startswith("Relatório de Gestão Fiscal")):
                    continue  # bimestres 1 a 5 do RREO e o resto não entram no coletor
                datas.append(date.fromisoformat(item["data_status"][:10]).isoformat())
                if rreo_anual:
                    anos_com_rreo.append(ano)
        marca = f"{max(datas)}|{len(datas)}" if datas else "sem-entregas|0"
        return Sentinela(marca, str(max(anos_com_rreo)) if anos_com_rreo else None)

    # --- TSE ---------------------------------------------------------------------------------------

    def _tse(self) -> Sentinela:
        vigentes = eleicoes_vigentes(self._hoje)
        marca = "|".join(f"{cargo}={ano}" for cargo, ano in sorted(vigentes.items()))
        return Sentinela(marca, str(max(vigentes.values())), proxima_posse(self._hoje).isoformat())
