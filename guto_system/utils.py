"""Funções utilitárias compartilhadas entre os módulos do GUTO."""
from datetime import date


def ano_atual():
    """Ano corrente como texto (usado como padrão de período letivo).

    Por ser uma função (e não um valor calculado na importação), o padrão
    acompanha a virada do ano e não gera migrações novas a cada ano.
    """
    return str(date.today().year)
