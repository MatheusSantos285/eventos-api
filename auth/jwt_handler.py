import time
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException, status
from jose import jwt, JWTError

# Em produção, esta chave deve ser injetada via variável de ambiente (CI/CD / AWS Secrets / Vault)
SECRET_KEY = "HI5HL3V3L$3CR3T_EVENTOS_API_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: str, role: str = "participante", mfa_verified: bool = False, scope: str="") -> str:
    """Cria um token JWT assinado contendo expiração, role e status de MFA."""
    payload = {
        "sub": user_id,  # Identificador único do usuário (UUID sugerido)
        "role": role,  # Papel do usuário (ex: participante, organizador, admin)
        "mfa_verified": mfa_verified,  # Indica se o usuário passou pela autenticação multifator,
        "scope": scope,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_access_token(token: str) -> Dict[str, Any]:
    """Decodifica e valida a assinatura e expiração de um JWT."""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Garante que o token não expirou
        if decoded_token.get("exp") < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado. Autentique-se novamente."
            )
        return decoded_token
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou assinatura corrompida."
        )