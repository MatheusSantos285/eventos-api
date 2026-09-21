import re
from typing import List, Any, Coroutine, Sequence
from fastapi import APIRouter, Body, HTTPException, status, Request, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.templating import Jinja2Templates
from auth.jwt_handler import verify_access_token
from auth.authenticate import get_current_user
from database.events import events_db
from config.rate_limiter import limiter
from sqlmodel import Session, select
from database.connection import get_session
from models.events import Event, EventCreate, EventPublicResponse, EventUpdateSchema, CommentSchema

event_router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

templates = Jinja2Templates(directory="templates")

# Instancia o esquema OAuth2 declarando os escopos disponíveis na API
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/user/login",
    scopes={
        "events:write": "Permite criar e modificar eventos",
        "events:read": "Permite visualizar e exportar eventos"
    }
)

async def verify_scopes(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> dict:
    """Verifica se o token possui TODOS os escopos exigidos pela rota."""
    payload = verify_access_token(token)

    # Extrai os escopos do token JWT (separados por espaço no padrão OAuth2)
    token_scopes = payload.get("scope", "").split()

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Escopo '{scope}' é necessário para esta operação (Violação de Contrato)."
            )
    return payload  # Retorna o payload para extrairmos o 'sub' depois

# =========================================================================
# EXERCÍCIO 1 - TP3: Rota de Busca (Vulnerável vs Segura)
# =========================================================================

@event_router.get("/search-vulnerable")
async def search_events_vulnerable(name: str):
    """
    SIMULAÇÃO DE VULNERABILIDADE.
    Demonstra a falha estrutural de concatenar parâmetros diretamente na query.
    """
    # Concatenação direta permitindo injeção de SQL ou quebra de sintaxe
    query_simulada = f"SELECT * FROM events WHERE name = '{name}'"

    return {
        "warning": "Esta rota é propositalmente vulnerável a SQL Injection.",
        "query_executada": query_simulada,
        "payload_recebido": name
    }

def validate_search_query(name: str) -> str:
    """
    Dependency Injection para validação de Input via Allow-List.
    Permite apenas letras, números e espaços, bloqueando caracteres especiais.
    """
    if not re.match(r"^[a-zA-Z0-9\s]+$", name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parâmetro de busca inválido. Apenas caracteres alfanuméricos e espaços são permitidos (Security Gate Block)."
        )
    return name


@event_router.get("/search")
async def search_events_secure(name: str = Depends(validate_search_query), session: Session = Depends(get_session)):
    """Rota Segura utilizando query parametrizada do SQLModel (Prevenção a SQLi)"""
    # O SQLModel nativamente trata a string evitando injeção
    statement = select(Event).where(Event.title.like(f"%{name}%"))
    resultados = session.exec(statement).all()

    return {
        "mensagem": "Busca processada de forma segura com query parametrizada.",
        "resultados_encontrados": len(resultados),
        "data": resultados
    }

# --- ROTAS NORMAIS AQUI (retrieve_all_events, retrieve_event) ---
@event_router.get("/", response_model=List[Event])
@limiter.limit("60/minute")
async def retrieve_all_events(request: Request, session: Session = Depends(get_session)) -> Sequence[Event]:
    return session.exec(select(Event)).all()

@event_router.get("/{id}", response_model=Event)
async def retrieve_event(id: int, session: Session = Depends(get_session)):
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado")
    return event

# --- NOVAS ROTAS COM PROTEÇÃO DE ESCOPO (M2M) ---
@event_router.get("/export/m2m", dependencies=[Security(verify_scopes, scopes=["events:read"])])
async def export_events(session: Session = Depends(get_session)):
    """Rota de leitura: Parceiro M2M consegue acessar (exige apenas 'events:read')"""
    return {
        "message": "Dados exportados com sucesso para o parceiro M2M",
        "data": session.exec(select(Event)).all()
    }


@event_router.post("/new", response_model=EventPublicResponse)
async def create_event(
        body: EventCreate,
        token_payload: dict = Security(verify_scopes, scopes=["events:write"]),
        session: Session = Depends(get_session)
):
    current_client_id = token_payload.get("sub")

    # Valida e converte o Pydantic Base para Tabela SQLModel
    db_event = Event.model_validate(body, update={"organizer": current_client_id})

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@event_router.put("/{event_id}", response_model=EventPublicResponse)
async def update_event(event_id: int, payload: EventUpdateSchema, current_user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # VALIDAÇÃO DE OWNERSHIP (Defesa BOLA)
    if str(event.organizer) != str(current_user_id):
        raise HTTPException(status_code=403, detail="Acesso Negado")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@event_router.delete("/{id}")
async def delete_event(id: int, current_user_id: str = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # VALIDAÇÃO DE OWNERSHIP
    if str(event.organizer) != str(current_user_id):
        raise HTTPException(status_code=403, detail="Acesso Negado")

    session.delete(event)
    session.commit()
    return {"message": "Evento deletado com sucesso"}

@event_router.get("/html/view")
async def render_events_html(request: Request):
    events_list = list(events_db.values())
    return templates.TemplateResponse(
        request=request,
        name="event_list.html",
        context={"events": events_list}
    )

@event_router.get("/html/view/{id}")
async def render_event_detail_html(request: Request, id: int):
    event = events_db.get(id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="event_detail.html",
        context={"event": event}
    )

# Rota para injetar o comentário (Stored XSS)
@event_router.post("/{id}/comments")
async def add_comment(id: int, payload: CommentSchema):
    event = events_db.get(id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    # Persiste o comentário malicioso em memória (Stored)
    event.comments.append(payload.text)
    return {"message": "Comentário registrado com sucesso"}