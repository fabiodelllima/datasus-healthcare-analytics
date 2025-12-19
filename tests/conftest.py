"""Configuração pytest para testes BDD."""


def pytest_configure(config):
    """Registrar markers customizados."""
    config.addinivalue_line("markers", "implemented: Funcionalidade implementada e testada")
    config.addinivalue_line("markers", "skip: Funcionalidade não implementada (pula teste)")
    config.addinivalue_line("markers", "wip: Work in Progress (planejado para versão futura)")
    config.addinivalue_line("markers", "future_v0.3.0: Funcionalidade planejada para v0.3.0")
    config.addinivalue_line("markers", "endpoint_disabled: Endpoint desabilitado na API externa")
