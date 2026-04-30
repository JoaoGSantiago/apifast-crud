from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import secao
from schemas import PedidoSchema
from models import Pedido

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos():
  return {"messagem": "voce acessou a rota de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(secao)):
  novo_pedido = Pedido(usuario=pedido_schema.usuario)
  session.add(novo_pedido)
  session.commit()
  return {"messagem": f"pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}
