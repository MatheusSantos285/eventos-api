from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, ConfigDict

# Tabela do BD
class Inscricao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    evento: str
    ingresso: str

# Schema de Validação BOPLA
class InscricaoCreateSchema(BaseModel):
    evento: str
    ingresso: str
    model_config = ConfigDict(extra='forbid')