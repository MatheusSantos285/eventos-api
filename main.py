from fastapi import FastAPI

from routes.events import event_router

app = FastAPI(
    title="Eventos API",
    description="API para gerenciamento de eventos",
    version="1.0.0"
)

""" 
### Exercício 1 - Status do Serviço ###
@app.get("/")
async def root_status():
    return {
        "status": "online",
        "message": "Serviço está operacional",
        "version": "1.0.0"
    }

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
"""

app.include_router(event_router, prefix="/events", tags=["Events"])
