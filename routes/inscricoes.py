from fastapi import APIRouter, Depends, HTTPException, status
from auth.authenticate import get_current_user
from database.inscricoes import inscricoes_db

inscricao_router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])

# 1, 2 e 3. Rota vulnerável a BOLA (IDOR) com exigência de JWT
@inscricao_router.get("/{id}")
async def get_inscricao_vulneravel(id: int, current_user: dict = Depends(get_current_user)):
    """
    Endpoint vulnerável: Retorna os dados da inscrição baseando-se apenas no ID da URL,
    sem validar se o usuário autenticado é o dono do recurso.
    """
    inscricao = inscricoes_db.get(id)

    if not inscricao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscrição não encontrada"
        )

    # AUSÊNCIA DE VALIDAÇÃO DE OWNERSHIP (Defesa contra BOLA)

    return inscricao