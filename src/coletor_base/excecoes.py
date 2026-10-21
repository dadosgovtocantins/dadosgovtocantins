"""
Exceções customizadas do framework ColetorBase.
PRD v4.2 §1.3 (RF-66, RF-71), RNF-S15.
"""


class ColetorError(Exception):
    """Classe base para todas as exceções de coletores."""

    pass


class ColetaBloqueadaError(ColetorError):
    """Lançada quando a fonte possui restrição em robots.txt ou termos de uso (RF-71)."""

    pass


class FonteIndisponivelError(ColetorError):
    """Lançada quando a fonte está fora do ar ou timeout (RF-66)."""

    pass


class ValidacaoError(ColetorError):
    """Lançada quando os dados extraídos falham nas regras de validação de schema/cobertura."""

    pass


class QualidadeSuspeitaError(ColetorError):
    """Lançada quando uma variação de indicador excede 3 sigmas (RF-65)."""

    pass


class ColetaNaoImplementadaError(ColetorError):
    """Lançada pelo coletor cuja coleta real ainda não existe: nenhum valor é gerado (RF-55)."""

    pass
