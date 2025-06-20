from __future__ import absolute_import, unicode_literals
import os
from celery import Celery  # ✅ Importa da lib celery, não do próprio core.celery

# Configura as settings do Django para o celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Configura celery para ler o settings do Django com prefixo 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tasks dentro de todos os apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
