# JetAide

AI chatbot to help manage personal goals (quit smoking, healthy eating, etc.)

## Stack

- **FastAPI** - Backend framework
- **PostgreSQL** - Database
- **Qdrant** - Vector memory
- **OpenRouter** - LLM API (dynamic model selection)
- **OAuth** - Google & Facebook authentication

## Setup

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Set up PostgreSQL

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16

# Create database
createdb jetaide
```

### 3. Set up Qdrant

```bash
# macOS
brew install qdrant
qdrant
```

Or use [Qdrant Cloud](https://cloud.qdrant.io/) (free tier available).

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

## API Docs

Visit http://localhost:8005/docs for Swagger UI.

## Endpoints

- `GET /auth/google/login` - Google OAuth login
- `GET /auth/facebook/login` - Facebook OAuth login
- `POST /chat` - Send message to chatbot
- `POST /chat/stream` - Stream chatbot response
- `GET /goals` - List user goals
- `POST /goals` - Create goal
