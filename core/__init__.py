from __future__ import absolute_import, unicode_literals

# Importa a instância do Celery assim que o Django inicia
from .celery import app as celery_app

__all__ = ('celery_app',)
