from fastapi import FastAPI, Request
from fastapi.middleware.cors import (CORSMiddleware)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from config.rate_limiter import limiter  # Importação da instância do limiter
from routes.admin import admin_router
from routes.events import event_router
from routes.inscricoes import inscricao_router
from routes.user import user_router
from database.connection import init_db

app = FastAPI(
    title="Eventos API",
    description="API para gerenciamento de eventos",
    version="2.0.0"
)

@app.on_event("startup")
def on_startup():
    """Evento de inicialização do aplicativo FastAPI."""
    init_db()  # Inicializa o banco de dados e cria as tabelas

# =========================================================================
# CONFIGURAÇÃO DE RATE LIMITING (SLOWAPI)
# =========================================================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =========================================================================
# 1. CONFIGURAÇÃO DE CORS (Allowlist Explícita)
# =========================================================================
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
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

app.include_router(event_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(inscricao_router)
