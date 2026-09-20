from pydantic import BaseModel, ConfigDict

class InscricaoCreateSchema(BaseModel):
    evento: str
    ingresso: str

    # Security Gate: Bloqueia injeção de propriedades indevidas (extra='forbid')
    model_config = ConfigDict(extra='forbid')

