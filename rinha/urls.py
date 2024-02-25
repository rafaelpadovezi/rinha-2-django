from django.contrib import admin
from django.urls import path
from rinha.apps.core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("clientes/<int:id>/extrato", views.get_extrato),
    path("clientes/<int:id>/transacoes", views.create_transacao),
]
