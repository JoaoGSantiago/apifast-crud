from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import secao
import bcrypt
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["/auth"])

@auth_router.get("/")
async def autenticar():
  """
  rota para fazer autenticação
  """
  return{"messagem": "Voce acessou a rota padrão de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(secao)):

  usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
  if usuario:
    raise HTTPException(status_code=400, detail="email do usuario ja cadastrado")
  else:
    senha_criptografada = bcrypt.hashpw(usuario_schema.senha.encode(), bcrypt.gensalt()).decode()
    novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada)
    session.add(novo_usuario)
    session.commit()
    return{"messagem": "usuario cadastrado"}



