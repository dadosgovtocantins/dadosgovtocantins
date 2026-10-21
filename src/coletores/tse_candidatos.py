"""Leitura comum do CSV de candidatos do TSE (consulta_cand) — usada pelo TO-GER-01 (Task 30).

Minimização (RNF-S05): só as colunas de COLUNAS saem da extração — CPF, e-mail, título e
nascimento nunca. Só o titular eleito do cargo entra; vice e não eleito ficam de fora (RF-11).
"""

import csv
import io
import zipfile
from datetime import UTC, date, datetime, timedelta, timezone
from typing import Any

from src.coletor_base.http import ClienteHTTP

URL_TSE = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip"
CARGOS = ("PREFEITO", "GOVERNADOR")
BRASILIA = timezone(timedelta(hours=-3))  # sem horário de verão desde 2019
COLUNAS = [
    "ANO_ELEICAO",
    "SG_UF",
    "SG_UE",
    "DS_CARGO",
    "SQ_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "DS_SIT_TOT_TURNO",
]


def hoje(agora: datetime | None = None) -> date:
    """Data de hoje em Brasília (a posse é em 1º de janeiro no Brasil, não em UTC)."""
    return (agora or datetime.now(UTC)).astimezone(BRASILIA).date()


def eleicoes_vigentes(ref: date) -> dict[str, int]:
    """Ano da eleição do mandato em curso em `ref`, por cargo (posse em 1º de janeiro do ano seguinte).

    Prefeitos: eleições em 2024, 2028...; governadores: 2022, 2026... O eleito de 2026 só vira o titular
    em 01/01/2027; até lá o titular é o de 2022 (e o de 2024 para prefeito).
    """
    ultimo = ref.year - 1  # a eleição mais recente que já deu posse
    return {
        "PREFEITO": ultimo - ultimo % 4,
        "GOVERNADOR": ultimo - (ultimo - 2) % 4,
    }


def proxima_posse(ref: date) -> date:
    """Próximo 1º de janeiro em que algum titular muda."""
    # a próxima eleição de cada cargo é 4 anos depois da vigente; a posse, no 1º de janeiro seguinte
    return min(date(ano + 5, 1, 1) for ano in eleicoes_vigentes(ref).values())


def eh_titular_to(linha: dict[str, str]) -> bool:
    return (
        linha["SG_UF"] == "TO"
        and linha["DS_CARGO"] in CARGOS
        and linha["DS_SIT_TOT_TURNO"] == "ELEITO"
    )


def baixar_titulares(http: ClienteHTTP, ref: date | None = None) -> bytes:
    """Baixa os zips do TSE da eleição vigente em `ref` (padrão: hoje) e devolve o CSV minimizado
    (UTF-8, ';') só com os titulares do TO."""
    saida = io.StringIO()
    escritor = csv.DictWriter(saida, COLUNAS, delimiter=";", extrasaction="ignore")
    escritor.writeheader()
    for cargo, ano in eleicoes_vigentes(ref or hoje()).items():
        with zipfile.ZipFile(io.BytesIO(http.get(URL_TSE.format(ano=ano)))) as z:
            texto = z.read(f"consulta_cand_{ano}_TO.csv").decode("latin-1")
        linhas = csv.DictReader(io.StringIO(texto), delimiter=";")
        escritor.writerows(r for r in linhas if eh_titular_to(r) and r["DS_CARGO"] == cargo)
    return saida.getvalue().encode("utf-8")


def ler_titulares(bruto: bytes) -> list[dict[str, str]]:
    leitor = csv.DictReader(io.StringIO(bruto.decode("utf-8")), delimiter=";")
    return [r for r in leitor if eh_titular_to(r)]


def montar_registro(
    r: dict[str, str], id_municipio: str | None, agora: str, id_fonte: str
) -> dict[str, Any]:
    prefeito = r["DS_CARGO"] == "PREFEITO"
    return {
        "id_titular": f"PREFEITO:{id_municipio}" if prefeito else "GOVERNADOR:TO",
        "id_municipio": id_municipio if prefeito else None,
        "cargo": r["DS_CARGO"],
        "nome_titular": r["NM_URNA_CANDIDATO"].strip(),
        "ano_eleicao": int(r["ANO_ELEICAO"]),
        "sq_candidato": r["SQ_CANDIDATO"],
        "url_foto": None,  # TO-GER-02 bloqueada por RF-71: o retrato não é coletado
        "fonte": "TSE",
        "id_fonte": id_fonte,
        "qualidade": "ok",
        "atualizado_em": agora,
    }
