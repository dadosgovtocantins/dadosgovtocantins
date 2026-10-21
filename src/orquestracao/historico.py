"""Histórico longo das séries com trava de 3σ (Task 35, passo 7).

O coletor diário busca poucos períodos (ex.: população "-3"); para medir a variação normal da série é
preciso mais história. Ela é buscada na mesma API, só para validar: não vai para o painel.
"""

from src.coletores.sidra import ColetorSidra
from src.orquestracao.painel import instanciar
from src.orquestracao.validacao import POLITICA_3SIGMA, serie_estadual

# fonte -> (períodos pedidos ao SIDRA, localidades). "-30" = últimos 30 anos; "-80" = últimos 80 trimestres.
BUSCA_HISTORICA = {
    "TO-TER-01": (
        "-30",
        "N3[17]",
    ),  # população do ESTADO (a série municipal somada tem a mesma forma)
    "TO-TER-03": ("-30", "N3[17]"),
    "TO-TER-07": ("-80", "N3[17]"),
}

assert set(BUSCA_HISTORICA) == set(POLITICA_3SIGMA)  # noqa: S101  (política e busca andam juntas)


def historico_estadual(id_fonte: str) -> list[list]:
    """[[rótulo, valor], ...] do estado em ordem cronológica. Falha de rede/formato propaga: sem a
    história a fonte não pode ser aceita."""
    periodos, localidades = BUSCA_HISTORICA[id_fonte]
    coletor = instanciar(id_fonte)
    assert isinstance(coletor, ColetorSidra)  # noqa: S101
    coletor.periodos, coletor.localidades = periodos, localidades
    return serie_estadual(coletor.transformar(coletor.extrair()))
