from slowapi import Limiter
from slowapi.util import get_remote_address

# Instancia o Limiter identificando os clientes pelo endereço IP
limiter = Limiter(key_func=get_remote_address)