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

    # Cria o JWT utilizando apenas o ID do usuário ("sub"), conforme exigido pela sua função jwt_handler.py
    access_token = create_access_token(user_exist["id"])

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }