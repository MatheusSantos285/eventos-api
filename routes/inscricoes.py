from fastapi import APIRouter, Depends, HTTPException, status
from auth.authenticate import get_current_user
from database.inscricoes import inscricoes_db
from sqlmodel import Session, select
from database.connection import get_session
from models.inscricao import Inscricao, InscricaoCreateSchema

inscricao_router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])

# 1, 2 e 3. Rota vulnerável a BOLA (IDOR) com exigência de JWT
@inscricao_router.get("/vulneravel/{id}")
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

async def get_owned_inscricao(id: int, current_user: dict = Depends(get_current_user),
                              session: Session = Depends(get_session)) -> Inscricao:
    inscricao = session.get(Inscricao, id)

    if not inscricao or str(inscricao.user_id) != str(current_user.get("sub")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    return inscricao

@inscricao_router.get("/{id}")
async def retrieve_inscricao(inscricao: Inscricao = Depends(get_owned_inscricao)):
    return inscricao

@inscricao_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_inscricao(payload: InscricaoCreateSchema, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    nova_inscricao = Inscricao(
        user_id=current_user.get("sub"),
        evento=payload.evento,
        ingresso=payload.ingresso
    )
    session.add(nova_inscricao)
    session.commit()
    session.refresh(nova_inscricao)
    return nova_inscricao