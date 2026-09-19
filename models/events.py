from typing import List, Optional
from pydantic import BaseModel

class Event(BaseModel):
    id: int
    title: str
    date: str
    organizer: str
    image: str
    description: str
    tags: List[str]
    location: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "We will be discussing the contents of the FastAPI book in this event.Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet"
            }
        }

# 1. Representação do que seria salvo no Banco de Dados (Contém dados sensíveis)
class EventInternal(BaseModel):
    title: str
    description: str
    organizer_id: int
    audit_token: str

# 2. O que o cliente pode ver (Exclui dados sensíveis)
class EventPublicResponse(BaseModel):
    title: str
    description: str

class EventUpdateSchema(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
