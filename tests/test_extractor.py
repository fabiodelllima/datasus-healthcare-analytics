"""
Testes para módulo Extract
"""

from src.extract.extractor import DataSUSExtractor


def test_extractor_init():
    """Testa inicialização do extractor"""
    extractor = DataSUSExtractor()
    assert isinstance(extractor, DataSUSExtractor)


# TODO: Adicionar mais testes no MVP
