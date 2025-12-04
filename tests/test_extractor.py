"""
Testes para módulo Extract
"""

import pytest
from src.extract.extractor import DataSUSExtractor

def test_extractor_init():
    """Testa inicialização do extractor"""
    extractor = DataSUSExtractor()
    assert extractor.sih is not None

# TODO: Adicionar mais testes no MVP
