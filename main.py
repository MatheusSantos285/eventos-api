from fastapi import FastAPI, Request
from fastapi.middleware.cors import (CORSMiddleware)
from routes.admin import admin_router
from routes.events import event_router
from routes.inscricoes import inscricao_router
from routes.user import user_router

app = FastAPI(
    title="Eventos API",
    description="API para gerenciamento de eventos",
    version="2.0.0"
)

# =========================================================================
# 1. CONFIGURAÇÃO DE CORS (Allowlist Explícita)
# =========================================================================
# Define explicitamente as origens permitidas (sem wildcard)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://parceiro-autorizado.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# =========================================================================
# 2. MIDDLEWARE DE CABEÇALHOS DE SEGURANÇA HTTP
# =========================================================================
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Previne ataques de downgrade (força HTTPS)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Previne Clickjacking bloqueando iframes não autorizados
    response.headers["X-Frame-Options"] = "DENY"
    # Previne MIME-Sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

app.include_router(event_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(inscricao_router)
