import uuid
from typing import List

from fastapi import APIRouter, Body, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from models.events import Event, EventPublicResponse, EventInternal
from database.database import events_db

event_router = APIRouter(
    tags=["Events"]
)
# Aponta para a pasta que criamos no Passo 3
templates = Jinja2Templates(directory="templates")

# --- Demonstração do Exercício 2 ---
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

@event_router.post("/new")
async def create_event(body: Event = Body(...)) -> dict:
    if body.id in events_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event with supplied ID already exists"
        )
    events_db[body.id] = body
    return {
        "message": "Event created successfully",
        "event": body
    }

@event_router.put("/{id}")
async def update_event(id: int, event_update: Event) -> dict:
    if id not in events_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    events_db[id] = event_update
    return {
        "message": "Event updated successfully",
        "event": event_update
    }
@event_router.delete("/{id}")
async def delete_event(id: int) -> dict:
    if id not in events_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist"
        )
    deleted_event = events_db.pop(id)
    return {
        "message": "Event deleted successfully",
        "deleted_event": deleted_event
    }

# --- Demonstração do Exercício 3 ---

# 1. Rota Segura (Com filtro Pydantic)
@event_router.post("/new-secure", response_model=EventPublicResponse)
async def create_event_secure():
    evento_salvo_no_banco = EventInternal(
        title="Meetup AppSec",
        description="Evento sobre segurança",
        organizer_id=404,
        audit_token=str(uuid.uuid4())
    )
    return evento_salvo_no_banco

# 2. Rota Vulnerável (Sem filtro Pydantic)
@event_router.post("/new-vulneravel")
async def create_event_vulnerable():
    evento_salvo_no_banco = EventInternal(
        title="Meetup Hacker",
        description="Evento vulnerável",
        organizer_id=404,
        audit_token=str(uuid.uuid4())
    )
    # Sem o response_model, o FastAPI serializa e devolve o objeto inteiro
    return evento_salvo_no_banco

# --- Demonstração do Exercício 4 ---
# Nova rota para renderizar a página HTML
@event_router.get("/html/view")
async def render_events_html(request: Request):
    # Converte o dicionário de eventos em uma lista para facilitar a iteração no template
    events_list = list(events_db.values())

    # O TemplateResponse precisa do "request" e dos dados ("events") para injetar no HTML
    return templates.TemplateResponse(
        request=request,
        name="event_list.html",
        context={"events": events_list}
    )

# --- Demonstração do Exercício 6 ---
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