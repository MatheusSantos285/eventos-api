from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON

class EventBase(SQLModel):
    title: str
    date: str
    image: str
    description: str
    location: str

# 1. Tabela de Banco de Dados (Herda de EventBase e SQLModel)
class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organizer: str = Field(index=True)
    # Salvando listas como JSON no SQLite
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    comments: List[str] = Field(default=[], sa_column=Column(JSON))

# 2. Esquemas de Requisição/Resposta Pydantic
class EventCreate(EventBase):
    tags: List[str] = []

class EventPublicResponse(BaseModel):
    id: int
    title: str
    description: str
    date: str
    location: str

class EventUpdateSchema(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None

class CommentSchema(BaseModel):
    text: str