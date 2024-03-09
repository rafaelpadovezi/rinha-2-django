from django.db import models
from django.db.models.functions import Now


class Cliente(models.Model):
    limite = models.IntegerField()
    saldo = models.IntegerField()


class Transacao(models.Model):
    valor = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1)
    descricao = models.CharField(max_length=10, null=False)
    realizada_em = models.DateTimeField(db_default=Now())
