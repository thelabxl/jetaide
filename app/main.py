from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth_router, chat_router, goals_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="JetAide",
    description="AI chatbot to help manage personal goals",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(goals_router)


@app.get("/")
async def root():
    return {"message": "Welcome to JetAide API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
