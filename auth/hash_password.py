from passlib.context import CryptContext

# Configuração do contexto de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera o hash seguro com salt de uma senha em texto claro."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado no banco de dados."""
        return pwd_context.verify(plain_password, hashed_password)

