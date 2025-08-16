# 42sp_transcendence

## Módulos completos
- Major module: Use a Framework as backend.
- Major module: Standard user management, authentication, users across tournaments.
- Major module: Implementing a remote authentication.
- Major module: Remote players
- Major module: Replacing Basic Pong with Server-Side Pong and Implementing an API.
- Major module: Add Another Game with User History and Matchmaking
- Major module: Introduce an AI Opponent.
- Major module: Live chat.

- Minor module: Use a front-end framework or toolkit.
- Minor module: Use a database for the backend.
- Minor module: Multiple language supports
- Minor module: Server-Side Rendering (SSR) Integration.
- Minor module: Expanding Browser Compatibility.
- Minor module: Support on all devices.

## Módulos para finalizar
- Minor module: User and Game Stats Dashboards.
- Minor module: Add accessibility for Visually Impaired Users.


# Deploy no Railway

1. Crie um novo projeto no Railway e conecte este repositório.
2. Configure as variáveis de ambiente no painel do Railway conforme o arquivo `.env.example`.
3. O Railway detectará o `Procfile` automaticamente.
4. O banco de dados PostgreSQL pode ser adicionado como plugin no Railway. As variáveis de conexão serão preenchidas automaticamente.
5. Certifique-se de rodar as migrações após o deploy:
	Vá em "Deployments" > "New Deployment Command" e adicione:
	```
	python manage.py migrate
	python manage.py collectstatic --noinput
	```
6. O projeto será servido via Daphne (ASGI) na porta definida pelo Railway.

Veja `.env.example` para as variáveis necessárias.
