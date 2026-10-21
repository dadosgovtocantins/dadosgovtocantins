"""Regras que decidem se uma coleta é aceita inteira ou recusada inteira (Task 35, passo 7).

Decisões do Bruno (21/10/2026):
  - IBGE e TSE: 139 municípios (100%), porque a publicação é simultânea.
  - SICONFI: o estado é obrigatório; município atrasado não bloqueia a atualização (o piso é preservado
    na mesclagem, ver painel.mesclar_indicador).
  - Trava de 3σ só em agregados estaduais e séries estruturais (estado, população), aplicada à VARIAÇÃO entre
    períodos e não ao nível; municipais voláteis (PAM, PPM, PIB e receita municipais) só têm integridade.

O backtest nas séries reais (tests/orquestracao/test_validacao.py) mostrou que o 3σ puro marcaria valores
legítimos (quebras do Censo na população, Covid na desocupação): por isso a variação também precisa passar de
um piso (10% ou 6 p.p.) para ser suspeita. Com o piso, 0 de 90 variações históricas são marcadas.
"""

import math
import re
from collections import defaultdict
from collections.abc import Callable
from itertools import pairwise
from typing import Any

from src.coletor_base.excecoes import ValidacaoError
from src.coletor_base.validacao import checar_variacao_3_sigma, validar_titulares
from src.coletores.depara_tse_ibge import DEPARA_TSE_IBGE
from src.orquestracao.fontes import TITULARES, TOTAL_MUNICIPIOS

MUNICIPIOS_TO = frozenset(DEPARA_TSE_IBGE.values())
MIN_HISTORICO = (
    3  # variações anteriores necessárias (a função checar_variacao_3_sigma não trava com menos)
)

# fonte -> (indicador, modo da variação, piso). "pct" = variação percentual; "abs" = diferença (p.p. para taxas).
POLITICA_3SIGMA: dict[str, tuple[str, str, float]] = {
    "TO-TER-01": ("populacao_residente", "pct", 10.0),
    "TO-TER-03": ("pib_estadual", "pct", 10.0),
    "TO-TER-07": ("taxa_desocupacao", "abs", 6.0),
}


class ColetaRecusada(ValueError):
    """A coleta não passou na validação: nada dela é publicado. `suspeito` = reprovada pelo 3σ."""

    def __init__(self, motivo: str, suspeito: bool = False):
        super().__init__(motivo)
        self.suspeito = suspeito


# --- 3σ sobre a variação entre períodos ---------------------------------------------------------


def variacoes(serie: list[list], modo: str) -> list[tuple[str, float]]:
    """[(rótulo, variação)] entre períodos consecutivos; em "pct" pula base zero (sem dividir por zero)."""
    if modo not in ("pct", "abs"):
        raise ValueError(f"modo de variação desconhecido: {modo!r} (use 'pct' ou 'abs')")
    saida = []
    for (_, anterior), (rotulo, atual) in pairwise(serie):
        if modo == "abs":
            saida.append((rotulo, atual - anterior))
        elif anterior != 0:
            saida.append((rotulo, (atual - anterior) / abs(anterior) * 100))
    return saida


def classificar_ponto(nova: float, historico: list[float], piso: float) -> str:
    """ "suspeito" só se estiver fora de 3σ do histórico E variar mais que o piso; histórico curto não trava."""
    if len(historico) < MIN_HISTORICO or abs(nova) <= piso:
        return "ok"
    return checar_variacao_3_sigma(nova, historico)


def checar_serie(serie: list[list], modo: str, piso: float) -> dict[str, Any]:
    """Avalia a variação do ÚLTIMO ponto contra as anteriores da série."""
    vs = variacoes(serie, modo)
    if len(vs) < MIN_HISTORICO + 1:
        return {
            "status": "ok",
            "avaliado": False,
            "rotulo": serie[-1][0] if serie else None,
            "variacao": None,
        }
    rotulo, nova = vs[-1]
    return {
        "status": classificar_ponto(nova, [v for _, v in vs[:-1]], piso),
        "avaliado": True,
        "rotulo": rotulo,
        "variacao": nova,
    }


def checar_novos(serie: list[list], novos: set[str], modo: str, piso: float) -> dict[str, Any]:
    """Avalia TODA variação que termina num período recém-coletado (inclui a emenda com o histórico), cada
    uma contra as anteriores. Devolve a primeira suspeita, ou o último ponto avaliado se todos passam."""
    vs = variacoes(serie, modo)
    resultado = {"status": "ok", "avaliado": False, "rotulo": None, "variacao": None}
    for t, (rotulo, valor) in enumerate(vs):
        if rotulo not in novos or t < MIN_HISTORICO:
            continue
        status = classificar_ponto(valor, [v for _, v in vs[:t]], piso)
        resultado = {"status": status, "avaliado": True, "rotulo": rotulo, "variacao": valor}
        if status == "suspeito":
            break
    return resultado


def backtest(serie: list[list], modo: str, piso: float) -> dict[str, Any]:
    """Aplica a regra a cada ponto histórico (janela que cresce): quais teriam sido marcados."""
    vs = variacoes(serie, modo)
    marcados = [
        {"rotulo": vs[t][0], "variacao": vs[t][1]}
        for t in range(MIN_HISTORICO, len(vs))
        if classificar_ponto(vs[t][1], [v for _, v in vs[:t]], piso) == "suspeito"
    ]
    avaliados = max(len(vs) - MIN_HISTORICO, 0)
    return {
        "avaliados": avaliados,
        "marcados": marcados,
        "percentual": 100 * len(marcados) / avaliados if avaliados else 0.0,
    }


def _chave_periodo(rotulo: str) -> tuple[int, int]:
    """'2025' -> (2025, 0); '2T2026' -> (2026, 2): ordem cronológica de rótulos anuais e trimestrais."""
    trimestre = re.fullmatch(r"(\d)T(\d{4})", rotulo)
    return (int(trimestre.group(2)), int(trimestre.group(1))) if trimestre else (int(rotulo[:4]), 0)


def mesclar_por_rotulo(historico: list[list], nova: list[list]) -> list[list]:
    por_rotulo = {r: v for r, v in [*historico, *nova]}  # o valor novo vence
    return [[r, por_rotulo[r]] for r in sorted(por_rotulo, key=_chave_periodo)]


def serie_estadual(registros: list[dict[str, Any]]) -> list[list]:
    """Série do estado [[rótulo, valor]]: o registro estadual, ou a soma dos municípios em cada período."""
    soma: dict[str, float] = defaultdict(float)
    rotulos: dict[str, str] = {}
    estadual = any(r["id_municipio"] is None for r in registros)
    for r in registros:
        if estadual and r["id_municipio"] is not None:
            continue
        soma[r["periodo_ref"]] += r["valor_num"]
        rotulos[r["periodo_ref"]] = r["valor_texto"] or r["periodo_ref"][:4]
    return [[rotulos[p], round(soma[p], 3)] for p in sorted(soma)]


# --- cobertura e integridade --------------------------------------------------------------------


def _numero_finito(valor: Any) -> bool:
    return not isinstance(valor, bool) and isinstance(valor, int | float) and math.isfinite(valor)


def validar_cobertura_ibge(id_fonte: str, registros: list[dict[str, Any]]) -> None:
    """IBGE: 139 municípios em CADA período (ou 1 registro estadual), valores finitos, sem duplicata."""
    if not registros:
        raise ColetaRecusada(f"{id_fonte}: a fonte não devolveu nenhum registro")
    por_periodo: dict[str, list[str | None]] = defaultdict(list)
    vistos = set()
    for r in registros:
        mun, periodo, valor = r["id_municipio"], r["periodo_ref"], r["valor_num"]
        if not _numero_finito(valor):
            raise ColetaRecusada(
                f"{id_fonte}: {mun or 'estado'} em {periodo} não tem número finito ({valor!r})"
            )
        if (mun, periodo) in vistos:
            raise ColetaRecusada(
                f"{id_fonte}: registro duplicado de {mun or 'estado'} em {periodo}"
            )
        vistos.add((mun, periodo))
        if mun is not None and mun not in MUNICIPIOS_TO:
            raise ColetaRecusada(f"{id_fonte}: município fora dos {TOTAL_MUNICIPIOS}: {mun}")
        por_periodo[periodo].append(mun)
    municipal = any(m is not None for ms in por_periodo.values() for m in ms)
    for periodo, ms in sorted(por_periodo.items()):
        if municipal and (None in ms or len(ms) != TOTAL_MUNICIPIOS):
            raise ColetaRecusada(
                f"{id_fonte}: {len(ms)} municípios em {periodo} (esperado {TOTAL_MUNICIPIOS})"
            )


def validar_rcl(registros: list[dict[str, Any]]) -> None:
    """SICONFI: o estado é obrigatório em cada exercício; município atrasado NÃO bloqueia (piso na mesclagem)."""
    if not registros:
        raise ColetaRecusada("TO-REC-02: a fonte não devolveu nenhum registro")
    vistos: set[tuple[str | None, str]] = set()
    exercicios: dict[str, bool] = {}
    for r in registros:
        mun, ano, valor = r["id_municipio"], r["periodo_ref"][:4], r["valor_num"]
        if not _numero_finito(valor) or valor <= 0:
            raise ColetaRecusada(
                f"TO-REC-02: RCL inválida ({valor!r}) de {mun or 'estado'} em {ano}"
            )
        if mun is not None and mun not in MUNICIPIOS_TO:
            raise ColetaRecusada(f"TO-REC-02: município fora dos {TOTAL_MUNICIPIOS}: {mun}")
        if (mun, ano) in vistos:
            raise ColetaRecusada(f"TO-REC-02: registro duplicado de {mun or 'estado'} em {ano}")
        vistos.add((mun, ano))
        exercicios[ano] = exercicios.get(ano, False) or mun is None
    sem_estado = sorted(a for a, tem in exercicios.items() if not tem)
    if sem_estado:
        raise ColetaRecusada(
            f"TO-REC-02: o estado não tem RCL no exercício {', '.join(sem_estado)}"
        )


def _validar_titulares(registros: list[dict[str, Any]]) -> None:
    """TSE: 139 prefeitos (100%) e 1 governador, sem duplicata (validar_titulares) e nomes preenchidos."""
    try:
        validar_titulares(registros, set(MUNICIPIOS_TO))
    except ValidacaoError as erro:
        raise ColetaRecusada(f"{TITULARES}: {erro}") from erro
    prefeitos = {r["id_municipio"] for r in registros if r["cargo"] == "PREFEITO"}
    if len(prefeitos) != TOTAL_MUNICIPIOS:
        faltam = sorted(MUNICIPIOS_TO - prefeitos)[:3]
        raise ColetaRecusada(
            f"{TITULARES}: {len(prefeitos)} prefeitos (esperado {TOTAL_MUNICIPIOS}); faltam {faltam}..."
        )


def validar_fonte(
    id_fonte: str, registros: list[dict[str, Any]], historico: Callable[[str], list[list]]
) -> None:
    """Levanta ColetaRecusada se a coleta não puder ser publicada. `historico(id_fonte)` só é chamado
    onde há trava de 3σ; erro ao obtê-lo propaga (a fonte não é aceita sem a checagem)."""
    if id_fonte == TITULARES:
        return _validar_titulares(registros)
    if id_fonte == "TO-REC-02":
        return validar_rcl(registros)
    validar_cobertura_ibge(id_fonte, registros)
    politica = POLITICA_3SIGMA.get(id_fonte)
    if politica is None:
        return None
    _indicador, modo, piso = politica
    nova = serie_estadual(registros)
    completa = mesclar_por_rotulo(historico(id_fonte), nova)
    r = checar_novos(completa, {rotulo for rotulo, _ in nova}, modo, piso)
    if r["status"] == "suspeito":
        unidade = "%" if modo == "pct" else " p.p."
        raise ColetaRecusada(
            f"{id_fonte}: variação de {r['variacao']:+.1f}{unidade} em {r['rotulo']} fora de 3σ do histórico "
            f"(piso {piso:g}{unidade}); o dado não foi publicado",
            suspeito=True,
        )
    return None
