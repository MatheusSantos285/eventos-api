# Eventos API

Esta é uma API REST construída com FastAPI para o gerenciamento de eventos. O projeto segue uma arquitetura modular para facilitar a manutenção, o isolamento de domínios e o *onboarding* de novos desenvolvedores.

## Estrutura do Projeto e Responsabilidades

Para que o código escale de forma limpa, as responsabilidades estão divididas nos seguintes módulos:

*   **`models/`**: Contém os modelos de dados e esquemas de validação utilizando Pydantic. Aqui ficam definidos os formatos de entrada (o que a API recebe) e os `response_models` (os filtros de saída, garantindo que dados internos não vazem).
*   **`routes/`**: Concentra os controladores (`APIRouter`) e a definição dos endpoints RESTful da aplicação. É responsável por receber a requisição HTTP, chamar a lógica necessária e devolver a resposta adequada. Não deve conter regras de negócio complexas ou conexão direta com banco de dados.
*   **`database/`**: Módulo dedicado à camada de persistência de dados. Atualmente utiliza simulação em memória, mas é o local correto para futuras configurações de ORM (como SQLAlchemy) e lógicas de CRUD no banco de dados.
*   **`main.py`**: Ponto de entrada (entrypoint) da aplicação. Responsável por inicializar o FastAPI, configurar middlewares e registrar (incluir) os routers dos diferentes domínios do sistema.