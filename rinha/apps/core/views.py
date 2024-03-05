from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rinha.apps.core.models import Cliente
from rinha.apps.core.models import Transacao
from django.db import transaction
from rinha.apps.core.serializers import TransacaoSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_extrato(request: Request, id: int) -> Response:
    clientes = Cliente.objects.filter(pk=id).values("limite", "saldo")
    if len(clientes) == 0:
        return Response({"message": "Cliente não encontrado"}, status=404)
    cliente = clientes[0]
    transacoes = Transacao.objects.order_by("-id").filter(cliente__id=id)[:10].values()

    return Response(
        {
            "saldo": {
                "limite": cliente["limite"],
                "total": cliente["saldo"],
            },
            "ultimas_transacoes": transacoes,
        }
    )


@api_view(["POST"])
def create_transacao(request: Request, id: int) -> Response:
    serializer = TransacaoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=422)

    transacao = serializer.validated_data
    valor_transacao = (
        transacao["valor"] if transacao["tipo"] == "c" else transacao["valor"] * -1
    )

    with transaction.atomic():
        cliente = Cliente.objects.select_for_update().get(pk=id)
        if cliente.saldo + valor_transacao < cliente.limite * -1:
            return Response({"message": "Saldo insuficiente"}, status=422)

        cliente.saldo += valor_transacao
        cliente.save()
        Transacao.objects.create(
            cliente=cliente,
            valor=transacao["valor"],
            tipo=transacao["tipo"],
            descricao=transacao["descricao"],
        )
    return Response({"saldo": cliente.saldo, "limite": cliente.limite})
