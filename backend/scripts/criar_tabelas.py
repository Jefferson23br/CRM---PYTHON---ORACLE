"""Script para criar tabelas via SQLAlchemy (desenvolvimento)."""

from app.database import Base, engine
from app.models import (  # noqa: F401 — importa modelos para registrar no metadata
    Cliente,
    Empresa,
    Mensagem,
    TokenRecuperacaoSenha,
    TopicoCRM,
    Usuario,
)


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")


if __name__ == "__main__":
    criar_tabelas()
