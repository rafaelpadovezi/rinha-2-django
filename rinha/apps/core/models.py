from django.db import models


class Cliente(models.Model):
    limite = models.IntegerField()
    saldo = models.IntegerField()


class Transacao(models.Model):
    TIPO_CHOICES = {
        "c": "Crédito",
        "d": "Débito",
    }
    valor = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    realizada_em = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=10, null=False)
