from fastapi import FastAPI

from routes.admin import admin_router
from routes.events import event_router
from routes.inscricoes import inscricao_router
from routes.user import user_router

app = FastAPI(
    title="Eventos API",
    description="API para gerenciamento de eventos",
    version="2.0.0"
)

app.include_router(event_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(inscricao_router)
