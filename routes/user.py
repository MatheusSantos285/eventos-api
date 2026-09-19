from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.users import users_db

user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@user_router.post("/login")
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends()) -> dict:
    # A rota /login verifica a existência do usuário e valida se as senhas coincidem para autorizar o acesso ou levantar uma exceção.
    user_exist = users_db.get(user.username)

    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Valida se a senha em plain-text informada bate com o Hash salvo utilizando a classe importada
    if not HashPassword.verify_password(user.password, user_exist["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    if user_exist["role"] == "admin":
        return {
            "mfa_required": True,
            "message": "Usuário admin requer autenticação multifator (MFA). Por favor, forneça o código MFA.",
            "username": user_exist["email"]
        }

    # Cria o JWT utilizando apenas o ID do usuário ("sub"), conforme exigido pela sua função jwt_handler.py
    access_token = create_access_token(user_id = user_exist["id"], role = user_exist["role"])

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@user_router.post("/login/mfa-verify")
async def verify_mfa(username: str, mfa_code: str) -> dict:
    """Validação do segundo fator de autenticação (MFA) para o papel de administrador."""
    user_exist = users_db.get(username)

    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if user_exist["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não elegível para MFA."
        )

    if user_exist["mfa_secret"] != mfa_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código MFA inválido."
        )

    # Se o código MFA estiver correto, cria o JWT com a flag mfa_verified = True
    access_token = create_access_token(user_id=user_exist["id"], role=user_exist["role"], mfa_verified=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Autenticação multifator (MFA) bem-sucedida."
    }