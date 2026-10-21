"""
Fixtures dos coletores IBGE (Task 28): respostas REAIS da API SIDRA, gravadas em 2026-10-14
pelo próprio extrair() de cada coletor (tests/fixtures/gravadas/). Os testes rodam sem rede.
Para regravar: chamar coletor.extrair() e salvar os bytes no mesmo arquivo.
"""

from pathlib import Path

GRAVADAS = Path(__file__).parent / "gravadas"


def _gravada(nome: str) -> bytes:
    return (GRAVADAS / nome).read_bytes()


def fixture_populacao() -> bytes:
    """SIDRA 6579, população residente estimada, 2024 a 2026 (TO-TER-01)."""
    return _gravada("sidra_to_ter_01.json")


def fixture_pib_municipal() -> bytes:
    """SIDRA 5938, PIB municipal a preços correntes, 2019 a 2023 (TO-TER-02)."""
    return _gravada("sidra_to_ter_02.json")


def fixture_pib_estadual() -> bytes:
    """SIDRA 5938, PIB do Tocantins, 2019 a 2023 (TO-TER-03)."""
    return _gravada("sidra_to_ter_03.json")


def fixture_malha_territorial() -> bytes:
    """SIDRA 4714, área da unidade territorial, Censo 2022 (TO-TER-04)."""
    return _gravada("sidra_to_ter_04.json")


def fixture_pam() -> bytes:
    """SIDRA 5457, valor da produção agrícola, total das lavouras, 2021 a 2025 (TO-TER-05)."""
    return _gravada("sidra_to_ter_05.json")


def fixture_ppm() -> bytes:
    """SIDRA 3939, efetivo de bovinos, 2021 a 2025 (TO-TER-06)."""
    return _gravada("sidra_to_ter_06.json")


def fixture_pnadc() -> bytes:
    """SIDRA 4099, taxa de desocupação do TO, 3T2025 a 2T2026 (TO-TER-07)."""
    return _gravada("sidra_to_ter_07.json")


def fixture_periodos(agregado: str) -> bytes:
    """GET /agregados/{agregado}/periodos: lista de períodos e data de modificação (gravada em 2026-10-21)."""
    return _gravada(f"ibge_periodos_{agregado}.json")


def fixture_calendario() -> bytes:
    """GET /calendario (21/10/2026 a 31/12/2027), recortado: PNAD Contínua trimestral (produto 9173) e 4 outros."""
    return _gravada("ibge_calendario.json")


def fixture_extrato_siconfi(ano: int) -> bytes:
    """SICONFI extrato_entregas do estado (ente 17) no exercício, recortado para RREO e RGF (gravado em 2026-10-21)."""
    return _gravada(f"siconfi_extrato_17_{ano}.json")
