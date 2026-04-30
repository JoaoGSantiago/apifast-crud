from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import Usuario
from dependencies import secao
import bcrypt
from schemas import LoginSchema, UsuarioSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from main import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

auth_router = APIRouter(prefix="/auth", tags=["auth"])
token_auth_scheme = HTTPBearer()

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
  data_expiracao = datetime.now(timezone.utc) + duracao_token
  credenciais = {"user_id": id_usuario, "exp": data_expiracao}
  encoded_jwt = jwt.encode(credenciais, SECRET_KEY, ALGORITHM)
  return encoded_jwt

def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
  return credentials.credentials

def verificar_token(token, session):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except JWTError:
    raise HTTPException(status_code=401, detail="Token invalido ou expirado")

  user_id = payload.get("user_id")
  if not user_id:
    raise HTTPException(status_code=401, detail="Token sem user_id")

  usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
  if not usuario:
    raise HTTPException(status_code=401, detail="Usuario nao encontrado")
  return usuario

def autenticar_usuario(email, senha, session):
  usuario = session.query(Usuario).filter(Usuario.email == email).first()
  if not usuario:
    return False
  senha_valida = bcrypt.checkpw(senha.encode(), usuario.senha.encode())
  if not senha_valida:
    return False
  return usuario


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(secao)):

  usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
  if usuario:
    raise HTTPException(status_code=400, detail="Email do usuario ja cadastrado")
  senha_criptografada = bcrypt.hashpw(usuario_schema.senha.encode(), bcrypt.gensalt()).decode()
  novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada)
  session.add(novo_usuario)
  session.commit()
  return {"mensagem": "Usuario cadastrado"}


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(secao)):
  usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
  if not usuario:
    raise HTTPException(status_code=400, detail="Usuario nao encontrado ou credenciais invalidas")
  access_token = criar_token(usuario.id)
  refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
  return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "Bearer",
  }

@auth_router.post("/refresh")
async def use_refresh_token(token: str = Depends(get_bearer_token), session: Session = Depends(secao)):
  usuario = verificar_token(token, session)
  access_token = criar_token(usuario.id)
  return {"access_token": access_token, "token_type": "Bearer"}

@auth_router.post("/logout")
async def logout(_: str = Depends(get_bearer_token)):
  return {"mensagem": "Logout realizado"}
