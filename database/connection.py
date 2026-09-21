from sqlmodel import create_engine, Session, SQLModel
from config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    """Gerador de sessões injetável via Depends do FastAPI"""
    with Session(engine) as session:
        yield session

def init_db():
    """Inicializa o banco de dados e cria as tabelas"""
    SQLModel.metadata.create_all(engine)