from rest_framework import serializers
from rinha.apps.core.models import Transacao


class TransacaoSerializer(serializers.ModelSerializer):
    descricao = serializers.CharField(required=True, max_length=10)
    tipo = serializers.ChoiceField(choices=Transacao.TIPO_CHOICES)
    valor = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Transacao
        fields = ["valor", "tipo", "descricao"]
