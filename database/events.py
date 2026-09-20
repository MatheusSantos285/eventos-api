# Dicionário em memória para simular o banco de dados.
# Em um cenário real, aqui ficaria a conexão com o PostgreSQL, MySQL, etc.,
# usando bibliotecas como SQLAlchemy ou SQLModel.

events_db = {
    1: {
      "id": 1,
      "title": "FastAPI XSS Meetup",
      "date": "2026-12-01",
      "organizer": "Organizador_A",
      "image": "https://example.com/image.png",
      "description": "Evento para testes de segurança (XSS).",
      "tags": ["segurança", "xss"],
      "location": "Rio de Janeiro"
    }
}