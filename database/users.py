from auth.hash_password import HashPassword

# Banco de dados simulado já com os usuários do teste
users_db = {
    "admin@empresa.com": {
        "id": "00000000-0000-0000-0000-000000000000",
        "email": "admin@empresa.com",
        "password": HashPassword.hash_password("admin_pass123"),
        "role": "admin",
        "mfa_secret": "123456"  # Código MFA simulado
    },
    "organizador_a@empresa.com": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "organizador_a@empresa.com",
        "password": HashPassword.hash_password("senha_segura_a"),
        "role": "organizador",
        "mfa_secret": None
    },
    "participante_c@empresa.com": {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "participante_c@empresa.com",
        "password": HashPassword.hash_password("senha_segura_c"),
        "role": "participante",
        "mfa_secret": None
    }
}