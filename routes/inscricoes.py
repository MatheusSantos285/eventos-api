from fastapi import APIRouter, Depends, HTTPException, status
from auth.authenticate import get_current_user
from database.inscricoes import inscricoes_db
from models.inscricao import InscricaoCreateSchema

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

# =========================================================================
# 1. CENTRALIZAÇÃO DE BOLA (Security Gate / Middleware)
# =========================================================================
async def get_owned_inscricao(id: int, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Middleware/Dependência que centraliza a verificação de existência e propriedade (Ownership).
    """
    inscricao = inscricoes_db.get(id)

    # Se a inscrição não existe ou o usuário logado não é o dono, retorna HTTP 404.
    # Ocultar o erro 403 e usar 404 mitiga enumeração de IDs por atacantes.
    if not inscricao or str(inscricao.get("user_id")) != str(current_user.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscrição não encontrada."
        )

    return inscricao

# =========================================================================
# ROTAS BLINDADAS
# =========================================================================
@inscricao_router.get("/{id}")
async def retrieve_inscricao(inscricao: dict = Depends(get_owned_inscricao)):
    """
    Rota Protegida: O código da rota em si fica limpo.
    Toda a validação BOLA/Ownership foi delegada para o 'get_owned_inscricao'.
    """
    return inscricao

@inscricao_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_inscricao(payload: InscricaoCreateSchema, current_user: dict = Depends(get_current_user)):
    """
    Rota Protegida: Proteção BOPLA garantida pelo InscricaoCreateSchema.
    Se o cliente injetar um {"is_admin": true}, o Pydantic lança HTTP 422 automaticamente.
    """
    nova_inscricao = {
        "id": len(inscricoes_db) + 1,
        "user_id": current_user.get("sub"),
        "evento": payload.evento,
        "ingresso": payload.ingresso
    }
    inscricoes_db[nova_inscricao["id"]] = nova_inscricao
    return nova_inscricao