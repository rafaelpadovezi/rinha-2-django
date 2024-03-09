from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rinha.apps.core.models import Cliente
from rinha.apps.core.models import Transacao
from django.db import transaction
from django.db.models import F


@api_view(["GET"])
def get_extrato(request: Request, id: int) -> Response:
    try:
        with transaction.atomic():
            cliente = Cliente.objects.values("limite", "saldo").get(pk=id)
            transacoes = (
                Transacao.objects.order_by("-id")
                .filter(cliente__id=id)
                .values()[:10]
                .iterator()
            )
    except Cliente.DoesNotExist:
        return Response({"message": "Cliente não encontrado"}, status=404)
    ultimas_transacoes = []
    for transacao in transacoes:
        ultimas_transacoes.append(
            {
                "valor": transacao["valor"],
                "tipo": transacao["tipo"],
                "descricao": transacao["descricao"],
                "realizada_em": transacao["realizada_em"],
            }
        )

    return Response(
        {
            "saldo": {
                "limite": cliente["limite"],
                "total": cliente["saldo"],
            },
            "ultimas_transacoes": ultimas_transacoes,
        }
    )


@api_view(["POST"])
def create_transacao(request: Request, id: int) -> Response:
    transacao = request.data
    tipo = transacao.get("tipo")
    valor = transacao.get("valor")
    descricao = transacao.get("descricao")
    if tipo not in ["c", "d"]:
        return Response({"message": "Tipo inválido"}, status=422)
    if not isinstance(valor, int) or valor < 1:
        return Response({"message": "Valor inválido"}, status=422)
    if descricao is None or not (1 <= len(descricao) <= 10):
        return Response({"message": "Descrição inválida"}, status=422)
    valor_transacao = (
        transacao["valor"] if transacao["tipo"] == "c" else transacao["valor"] * -1
    )

    # with transaction.atomic(savepoint=False):
    # affected = Cliente.objects.filter(pk=id) \
    #     .filter(saldo__gt=F("limite") * -1 - valor_transacao) \
    #     .update(saldo=F("saldo") + valor_transacao)

    # cliente = Cliente.objects.filter(pk=id).values("limite", "saldo").first()
    # if cliente is None:
    #     return Response({"message": "Cliente não encontrado"}, status=404)
    # if affected == 0:
    #     return Response({"message": "Saldo insuficiente"}, status=422)

    # Transacao.objects.create(
    #     cliente_id=id,
    #     valor=transacao["valor"],
    #     tipo=transacao["tipo"],
    #     descricao=transacao["descricao"],
    # )
    # return Response({"saldo": cliente["saldo"], "limite": cliente["limite"]})

    with transaction.atomic(savepoint=False):
        cliente = Cliente.objects.select_for_update().filter(pk=id).first()
        if cliente is None:
            return Response({"message": "Cliente não encontrado"}, status=404)
        if cliente.saldo + valor_transacao < cliente.limite * -1:
            return Response({"message": "Saldo insuficiente"}, status=422)

        cliente.saldo += valor_transacao
        cliente.save(update_fields=["saldo"])
        new_transacao = Transacao(None, valor, id, tipo, descricao)
        new_transacao.save()
    return Response({"saldo": cliente.saldo, "limite": cliente.limite})
