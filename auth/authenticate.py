from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import verify_access_token

# Define a URL de onde as credenciais serão recuperadas para o login (fluxo local)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency Injection que extrai o ID do usuário do token JWT.
    Injetada nas rotas que exigem apenas autenticação (AuthN).
    """
    decoded = verify_access_token(token)
    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém identificação de assunto (sub)."
        )
    return user_id