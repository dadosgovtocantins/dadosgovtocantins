"""
Módulo de leitura e validação do Catálogo em dois níveis.
PRD v4.2 §1.4 (RF-80 a RF-84), Anexo B e Task 04.
"""

from dataclasses import dataclass

# Colunas obrigatórias da aba catalogo_fontes (40 colunas do Anexo B)
COLUNAS_FONTES_OBRIGATORIAS: list[str] = [
    "ID",
    "ÓRGÃO",
    "INDICADOR",
    "ÁREA",
    "SISTEMA",
    "O QUE REPRESENTA",
    "LINK PÚBLICO",
    "URL DA API",
    "ENDPOINT",
    "AUTENTICAÇÃO",
    "FORMATO",
    "CLASSE DE FORMATO",
    "PERIODICIDADE EXATA",
    "DEFASAGEM",
    "ÚLTIMA ATUALIZAÇÃO",
    "HISTÓRICO DISPONÍVEL",
    "NÍVEL GEOGRÁFICO",
    "GRANULARIDADE TEMPORAL",
    "UNIDADE DE MEDIDA",
    "RESPONSÁVEL PELO DADO",
    "FONTE PRIMÁRIA/SECUNDÁRIA",
    "TIPO DE FONTE",
    "FONTE ABERTA EQUIVALENTE",
    "PAINEL LAB63 RELACIONADO",
    "POWER BI DATASET ID",
    "POWER BI REPORT ID",
    "ACESSO PÚBLICO SEM CADASTRO?",
    "REUTILIZÁVEL?",
    "API PÚBLICA?",
    "DADOS REALMENTE ABERTOS?",
    "QUADRANTE",
    "ESCOPO",
    "LICENÇA DE USO",
    "RESTRIÇÃO ROBOTS/TERMOS",
    "MÉTODO DE COLETA",
    "STATUS DE VALIDAÇÃO",
    "NÍVEL DE CONFIABILIDADE",
    "CLASSIFICAÇÃO",
    "PRIORIDADE",
    "OBSERVAÇÕES TÉCNICAS",
]

# Colunas obrigatórias da aba catalogo_indicadores (12 colunas do Anexo B)
COLUNAS_INDICADORES_OBRIGATORIAS: list[str] = [
    "id_indicador",
    "id_fonte",
    "nome_exibicao",
    "definicao_cidadao",
    "unidade",
    "sentido",
    "tela",
    "ordem_card",
    "icone",
    "calculado",
    "formula",
    "status",
]

VALORES_SENTIDO_VALIDOS: set[str] = {"maior_melhor", "menor_melhor", "neutro"}
VALORES_TELA_VALIDOS: set[str] = {"municipio", "estado", "orgao"}
VALORES_STATUS_VALIDOS: set[str] = {"ativo", "homologacao", "descontinuado"}


@dataclass
class Fonte:
    id_fonte: str
    orgao: str
    classificacao: str  # A, B, C, D
    restricao_robots: str
    link_publico: str
    reutilizavel: str


@dataclass
class Indicador:
    id_indicador: str
    id_fonte: str
    nome_exibicao: str
    definicao_cidadao: str
    unidade: str
    sentido: str
    tela: str
    ordem_card: int
    icone: str
    calculado: bool
    formula: str | None
    status: str


class CatalogoValidationError(Exception):
    """Exceção lançada quando a validação do catálogo falha."""

    pass


def validar_catalogo_fontes(fontes: list[dict[str, str]]) -> dict[str, Fonte]:
    """
    Valida a lista de dicionários representando a aba catalogo_fontes.
    Retorna um dicionário id_fonte -> Fonte.
    """
    if not fontes:
        raise CatalogoValidationError("A aba catalogo_fontes está vazia.")

    # Verificar presença das colunas no primeiro registro
    primeiro = fontes[0]
    for col in COLUNAS_FONTES_OBRIGATORIAS:
        if col not in primeiro:
            raise CatalogoValidationError(f"Coluna obrigatória ausente em catalogo_fontes: '{col}'")

    ids_vistos: set[str] = set()
    mapa_fontes: dict[str, Fonte] = {}

    for idx, f in enumerate(fontes, start=2):
        fonte_id = f.get("ID", "").strip()
        if not fonte_id:
            raise CatalogoValidationError(f"Linha {idx}: ID da fonte ausente.")
        if fonte_id in ids_vistos:
            raise CatalogoValidationError(
                f"Linha {idx}: ID duplicado em catalogo_fontes: '{fonte_id}'."
            )
        ids_vistos.add(fonte_id)

        # Garantir preenchimento e data de RESTRIÇÃO ROBOTS/TERMOS
        restricao = f.get("RESTRIÇÃO ROBOTS/TERMOS", "").strip()
        if not restricao:
            raise CatalogoValidationError(
                f"Linha {idx} ({fonte_id}): Coluna 'RESTRIÇÃO ROBOTS/TERMOS' não pode estar em branco."
            )

        mapa_fontes[fonte_id] = Fonte(
            id_fonte=fonte_id,
            orgao=f.get("ÓRGÃO", "").strip(),
            classificacao=f.get("CLASSIFICAÇÃO", "").strip().upper(),
            restricao_robots=restricao,
            link_publico=f.get("LINK PÚBLICO", "").strip(),
            reutilizavel=f.get("REUTILIZÁVEL?", "").strip(),
        )

    return mapa_fontes


def validar_catalogo_indicadores(
    indicadores: list[dict[str, str]], mapa_fontes: dict[str, Fonte]
) -> list[Indicador]:
    """
    Valida a aba catalogo_indicadores garantindo integridade referencial com catalogo_fontes.
    """
    if not indicadores:
        raise CatalogoValidationError("A aba catalogo_indicadores está vazia.")

    primeiro = indicadores[0]
    for col in COLUNAS_INDICADORES_OBRIGATORIAS:
        if col not in primeiro:
            raise CatalogoValidationError(
                f"Coluna obrigatória ausente em catalogo_indicadores: '{col}'"
            )

    resultado: list[Indicador] = []
    fontes_com_indicador: set[str] = set()

    for idx, ind in enumerate(indicadores, start=2):
        id_ind = ind.get("id_indicador", "").strip()
        id_fonte = ind.get("id_fonte", "").strip()
        nome = ind.get("nome_exibicao", "").strip()
        definicao = ind.get("definicao_cidadao", "").strip()
        unidade = ind.get("unidade", "").strip()
        sentido = ind.get("sentido", "").strip().lower()
        tela = ind.get("tela", "").strip().lower()
        status = ind.get("status", "").strip().lower()
        calculado_raw = str(ind.get("calculado", "")).strip().upper()
        calculado = calculado_raw in ("TRUE", "1", "VERDADEIRO")
        formula = ind.get("formula", "").strip() or None

        if not id_ind:
            raise CatalogoValidationError(f"Linha {idx}: id_indicador ausente.")

        # Checagem de FK
        if id_fonte not in mapa_fontes:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): FK id_fonte '{id_fonte}' não existe em catalogo_fontes."
            )
        fontes_com_indicador.add(id_fonte)

        # Checagem de unidade única (sem vírgula/barra separando múltiplas)
        if "," in unidade or ";" in unidade:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): Coluna 'unidade' deve conter apenas uma unidade, valor recebido: '{unidade}'."
            )

        if sentido not in VALORES_SENTIDO_VALIDOS:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): 'sentido' inválido '{sentido}'. Válidos: {VALORES_SENTIDO_VALIDOS}"
            )

        if tela not in VALORES_TELA_VALIDOS:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): 'tela' inválida '{tela}'. Válidos: {VALORES_TELA_VALIDOS}"
            )

        if status not in VALORES_STATUS_VALIDOS:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): 'status' inválido '{status}'. Válidos: {VALORES_STATUS_VALIDOS}"
            )

        if calculado and not formula:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): 'calculado = TRUE' exige preenchimento da coluna 'formula'."
            )

        try:
            ordem_card = int(ind.get("ordem_card", "0"))
        except ValueError as err:
            raise CatalogoValidationError(
                f"Linha {idx} ({id_ind}): 'ordem_card' deve ser um inteiro."
            ) from err

        resultado.append(
            Indicador(
                id_indicador=id_ind,
                id_fonte=id_fonte,
                nome_exibicao=nome,
                definicao_cidadao=definicao,
                unidade=unidade,
                sentido=sentido,
                tela=tela,
                ordem_card=ordem_card,
                icone=ind.get("icone", "").strip(),
                calculado=calculado,
                formula=formula,
                status=status,
            )
        )

    # Regra de cobertura: Fontes classe A ou B devem ter pelo menos 1 indicador ligado
    for fonte_id, fonte in mapa_fontes.items():
        if fonte.classificacao in ("A", "B") and fonte_id not in fontes_com_indicador:
            raise CatalogoValidationError(
                f"Fonte de alta prioridade '{fonte_id}' (Classe {fonte.classificacao}) não possui nenhum indicador associado em catalogo_indicadores."
            )

    return resultado
