from django.contrib import admin

from rinha.apps.core.models import Cliente
from rinha.apps.core.models import Transacao

admin.site.register(Cliente)
admin.site.register(Transacao)
