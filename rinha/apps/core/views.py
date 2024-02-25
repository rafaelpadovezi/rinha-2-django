from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rinha.apps.core.models import Cliente
from rinha.apps.core.models import Transacao
from django.db import transaction
from rinha.apps.core.serializers import TransacaoSerializer


class TransacaoView(APIView):
    def post(self, request):
        pass


@api_view(["GET"])
def get_extrato(request: Request, id: int) -> Response:
    try:
        cliente = Cliente.objects.get(pk=id)
    except Cliente.DoesNotExist:
        return Response({"message": "Cliente não encontrado"}, status=404)
    transacoes = Transacao.objects.order_by("-id").filter(cliente__id=id)[:10]
    ultimas_transacoes = []
    for transacao in transacoes:
        ultimas_transacoes.append(
            {
                "valor": transacao.valor,
                "tipo": transacao.tipo,
                "descricao": transacao.descricao,
                "realizada_em": transacao.realizada_em,
            }
        )

    return Response(
        {
            "limite": cliente.limite,
            "saldo": cliente.saldo,
            "ultimas_transacoes": ultimas_transacoes,
        }
    )


@api_view(["POST"])
def create_transacao(request: Request, id: int) -> Response:
    serializer = TransacaoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

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
