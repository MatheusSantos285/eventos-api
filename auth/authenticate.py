from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import verify_access_token

# Define a URL de onde as credenciais serão recuperadas para o login (fluxo local)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency Injection que extrai o ID do usuário do token JWT.
    Injetada nas rotas que exigem apenas autenticação (AuthN).
    """
    return verify_access_token(token)

async def require_admin(claims: dict = Depends(get_current_user)) -> dict:
    """Garante que o usuário possui o papel admin E que passou pelo MFA."""
    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a Administradores do sistema (BFLA Block)."
        )
    if not claims.get("mfa_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação requer autenticação com Múltiplo Fator (MFA)."
        )
    return claims
