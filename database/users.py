from auth.hash_password import HashPassword

# Banco de dados simulado já com os usuários do teste
users_db = {
    "organizador_a@empresa.com": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "organizador_a@empresa.com",
        "password": HashPassword.hash_password("senha_segura_a")
    },
    "organizador_b@empresa.com": {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "organizador_b@empresa.com",
        "password": HashPassword.hash_password("senha_segura_b")
    }
}