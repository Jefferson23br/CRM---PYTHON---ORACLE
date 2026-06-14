from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import auth, clientes, empresas, mensagens, topicos, usuarios

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST do CRM Piloto — sistema multi-empresa para gestão de clientes, "
        "tópicos de atendimento e funil de vendas."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex_pattern,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_prefix

app.include_router(auth.router, prefix=api_prefix)
app.include_router(empresas.router, prefix=api_prefix)
app.include_router(usuarios.router, prefix=api_prefix)
app.include_router(clientes.router, prefix=api_prefix)
app.include_router(topicos.router, prefix=api_prefix)
app.include_router(mensagens.router, prefix=api_prefix)


@app.get("/")
def root():
    return {
        "nome": settings.app_name,
        "versao": "0.1.0",
        "status": "online",
        "documentacao": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM dual"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "database": str(exc)}
