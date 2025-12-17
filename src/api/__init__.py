"""Módulo de integração com APIs do ecossistema DataSUS.

Este módulo fornece ferramentas para inspeção e consulta de metadados
na API OpenDataSUS, permitindo descoberta de datasets e validação de
atualizações sem necessidade de download via FTP.
"""

from .datasus_inspector import OpenDataSUSInspector

__all__ = ["OpenDataSUSInspector"]
