"""
Модуль парсеров для различных площадок государственных закупок
"""

from .eis_parser import EISParser
from .suppliers_portal_parser import SuppliersPortalParser

__all__ = ['EISParser', 'SuppliersPortalParser']
