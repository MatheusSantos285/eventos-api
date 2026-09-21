from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str
    role: str = Field(default="participante")
    mfa_secret: Optional[str] = None