from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from rinha.settings import DATABASE_URL
from rinha.settings import DB_POOL_MAX_SIZE

logger = logging.getLogger(__name__)

pool = ConnectionPool(DATABASE_URL, open=True, min_size=5, max_size=DB_POOL_MAX_SIZE)

@api_view(["GET"])
def get_extrato(request: Request, id: int) -> Response:
    ultimas_transacoes = []
    cliente = None
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT c.limite, c.saldo, t.*
                FROM core_cliente c
                LEFT JOIN (
                    SELECT *
                    FROM core_transacao
                    ORDER BY id DESC
                    LIMIT 10
                ) t ON c.id = t.cliente_id
                WHERE c.id = %s;""", [id])
            for record in cur:
                if cliente is None:
                    cliente = {
                        "limite": record["limite"],
                        "saldo": record["saldo"],
                    }
                if record["valor"] is not None:
                    ultimas_transacoes.append({
                        "valor": record["valor"],
                        "tipo": record["tipo"],
                        "descricao": record["descricao"],
                        "realizado_em": record["realizada_em"],
                    })
    if cliente is None:
        return Response({"message": "Cliente não encontrado"}, status=404)

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

    with pool.connection() as conn:

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT c.limite, c.saldo FROM core_cliente c WHERE c.id = %s FOR UPDATE", [id])
            result = cur.fetchone()
            cliente = {
                "limite": result["limite"],
                "saldo": result["saldo"],
            }
            novo_saldo = cliente["saldo"] + valor_transacao
            if novo_saldo < cliente["limite"] * -1:
                return Response({"message": "Saldo insuficiente"}, status=422)
            cur.execute("UPDATE core_cliente SET saldo = %s WHERE id = %s", (novo_saldo, id))
            cur.execute(
                """INSERT INTO core_transacao (cliente_id, valor, tipo, descricao, realizada_em) 
                VALUES (%s, %s, %s, %s, 'now');
                """, (id, transacao["valor"], transacao["tipo"], transacao["descricao"]))

    return Response({"saldo": novo_saldo, "limite": cliente["limite"]})
