import uuid
import re
from typing import List
from fastapi import APIRouter, Body, HTTPException, status, Request, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.templating import Jinja2Templates

from auth.jwt_handler import verify_access_token
from models.events import Event, EventPublicResponse, EventInternal, EventUpdateSchema
from auth.authenticate import get_current_user
from database.events import events_db

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
async def search_events_secure(name: str = Depends(validate_search_query)):
    """
    ROTA SEGURA: O parâmetro 'name' passou pelo Security Gate (validate_search_query)
    que aplica o padrão Allow-List (Regex), evitando qualquer injeção maliciosa.
    """
    # Na prática, a query real no banco seria construída com parametrização (ORM/Driver):
    # ex: cursor.execute("SELECT * FROM events WHERE title LIKE :name", {"name": f"%{name}%"})
    query_segura = "SELECT * FROM events WHERE title LIKE :name (Parametrizado)"

    # Filtro simulado no dicionário em memória ignorando case
    resultados = [
        event for event in events_db.values()
        if name.lower() in event.title.lower()
    ]

    return {
        "mensagem": "Busca processada de forma segura.",
        "query_estrutural": query_segura,
        "resultados_encontrados": len(resultados),
        "data": resultados
    }

# --- ROTAS NORMAIS AQUI (retrieve_all_events, retrieve_event) ---
@event_router.get("/", response_model=List[Event])
async def retrieve_all_events() -> List[Event]:
    return list(events_db.values())

@event_router.get("/{id}", response_model=Event)
async def retrieve_event(id: int) -> Event:
    event = events_db.get(id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    return event

# --- NOVAS ROTAS COM PROTEÇÃO DE ESCOPO (M2M) ---
@event_router.get("/export/m2m", dependencies=[Security(verify_scopes, scopes=["events:read"])])
async def export_events():
    """Rota de leitura: Parceiro M2M consegue acessar (exige apenas 'events:read')"""
    return {
        "message": "Dados exportados com sucesso para o parceiro M2M",
        "data": list(events_db.values())
    }

@event_router.post("/new", response_model=EventPublicResponse)
async def create_event(
    body: Event = Body(...),
    token_payload: dict = Security(verify_scopes, scopes=["events:write"]) # Exige escopo de escrita
) -> dict:
    if body.id in events_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event with supplied ID already exists"
        )

    # Ao invés do get_current_user, extraímos o ID direto do payload validado pelo verify_scopes
    current_client_id = token_payload.get("sub")
    body.organizer = current_client_id

    events_db[body.id] = body
    return body

@event_router.put("/{event_id}", response_model=EventPublicResponse)
async def update_event(event_id: int, payload: EventUpdateSchema, current_user_id: str = Depends(get_current_user)) -> dict:
    """
    Rota protegida de edição de eventos.
    Previne ataques BOLA validando se o usuário autenticado é o dono do registro.
    """
    # 1. Recupera o evento solicitado na base de dados
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com ID {event_id} não encontrado."
        )

    # 2. VALIDAÇÃO DE OWNERSHIP (Defesa contra BOLA)
    if str(event.organizer) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado: Apenas o organizador dono do evento pode editá-lo."
        )

    # 3. Atualização segura do recurso iterando sobre os dados fornecidos
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    return event

@event_router.delete("/{id}")
async def delete_event(id: int, current_user_id: str = Depends(get_current_user)) -> dict:
    event = events_db.get(id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    # VALIDAÇÃO DE OWNERSHIP (Defesa contra BOLA)
    if str(event.organizer) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado: Apenas o organizador dono do evento pode deletá-lo."
        )

    deleted_event = events_db.pop(id)
    return {
        "message": "Event deleted successfully",
        "event": deleted_event
    }

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