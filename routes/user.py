from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.users import users_db
from config.rate_limiter import limiter
from sqlmodel import select, Session
from database.connection import get_session
from models.users import User
from auth.hash_password import HashPassword

user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@user_router.post("/seed")
async def seed_users(session: Session = Depends(get_session)):
    """Popula o banco SQLite com os usuários de teste."""
    usuarios = [
        User(id="00000000-0000-0000-0000-000000000000", email="admin@empresa.com",
             password=HashPassword.hash_password("admin_pass123"), role="admin", mfa_secret="123456"),
        User(id="11111111-1111-1111-1111-111111111111", email="organizador_a@empresa.com",
             password=HashPassword.hash_password("senha_segura_a"), role="organizador"),
        User(id="22222222-2222-2222-2222-222222222222", email="participante_c@empresa.com",
             password=HashPassword.hash_password("senha_segura_c"), role="participante"),
        User(id="33333333-3333-3333-3333-333333333333", email="parceiro_m2m@empresa.com",
             password=HashPassword.hash_password("senha_m2m"), role="parceiro_m2m")
    ]

    for u in usuarios:
        # Verifica se já não existe para evitar erro de duplicidade se você rodar o seed duas vezes
        if not session.get(User, u.id):
            session.add(u)

    session.commit()
    return {"msg": "Banco de dados populado com os usuários de teste!"}

@user_router.post("/login")
@limiter.limit("5/minute")
async def sign_user_in(request: Request, user: OAuth2PasswordRequestForm = Depends(),
                       session: Session = Depends(get_session)):
    # Busca real no banco de dados
    statement = select(User).where(User.email == user.username)
    user_exist = session.exec(statement).first()

    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Valida se a senha em plain-text informada bate com o Hash salvo utilizando a classe importada
    if not HashPassword.verify_password(user.password, user_exist.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    if user_exist.role == "admin":
        return {
            "mfa_required": True,
            "message": "Usuário admin requer autenticação multifator (MFA). Por favor, forneça o código MFA.",
            "username": user_exist.email
        }

    # Transforma a lista de escopos ['events:read'] em uma string 'events:read'
    scopes_string = " ".join(user.scopes)

    # Cria o JWT utilizando apenas o ID do usuário ("sub"), conforme exigido pela sua função jwt_handler.py
    access_token = create_access_token(user_id = user_exist.id, role = user_exist.role, scope = scopes_string)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@user_router.post("/login/mfa-verify")
async def verify_mfa(username: str, mfa_code: str, session: Session = Depends(get_session)) -> dict:
    """Validação do segundo fator de autenticação (MFA) para o papel de administrador."""

    statement = select(User).where(User.email == username)
    user_exist = session.exec(statement).first()

    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # CORREÇÃO: Utilizando notação de ponto
    if user_exist.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não elegível para MFA."
        )

    if user_exist.mfa_secret != mfa_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código MFA inválido."
        )

    # Cria o JWT com a flag mfa_verified = True
    access_token = create_access_token(user_id=str(user_exist.id), role=user_exist.role, mfa_verified=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Autenticação multifator (MFA) bem-sucedida."
    }