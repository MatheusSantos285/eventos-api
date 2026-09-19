from fastapi import APIRouter, Depends, HTTPException, status
from auth.authenticate import oauth2_scheme
from auth.jwt_handler import verify_access_token

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

def verify_admin_mfa(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Security Gate: Decodifica o token e valida Autorização Baseada em Regras (RBAC)
    e o status da Autenticação Multifator (MFA).
    """
    # 1. Valida a assinatura e expiração do token
    decoded_token = verify_access_token(token)

    # 2. Verifica se o usuário tem a role de administrador
    if decoded_token.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado: Privilégios de administrador obrigatórios."
        )

    # 3. Verifica se o desafio MFA foi concluído
    if not decoded_token.get("mfa_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado: Autenticação de múltiplos fatores (MFA) pendente."
        )

    return decoded_token


@admin_router.get("/dashboard")
async def get_admin_dashboard(current_admin: dict = Depends(verify_admin_mfa)):
    """
    Rota exclusiva para administradores com MFA verificado.
    """
    return {
        "message": "Acesso Autorizado. Bem-vindo ao Painel de Controle (Admin).",
        "admin_id": current_admin.get("sub"),
        "security_status": "MFA Validado"
    }