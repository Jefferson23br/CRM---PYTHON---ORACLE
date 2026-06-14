from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _oracle_enum(enum_class, length: int = 30):
    """Enum como VARCHAR — usa o .value (ex: ativa), não o nome (ATIVA)."""
    return Enum(
        enum_class,
        native_enum=False,
        length=length,
        values_callable=lambda enum: [item.value for item in enum],
    )


class TipoUsuario(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN_EMPRESA = "admin_empresa"
    GERENTE = "gerente"
    VENDEDOR = "vendedor"
    ATENDENTE = "atendente"
    VISUALIZADOR = "visualizador"


class StatusEmpresa(str, PyEnum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    SUSPENSA = "suspensa"


class StatusCliente(str, PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PROSPECTO = "prospecto"
    LEAD = "lead"


class StatusTopico(str, PyEnum):
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"


class PrioridadeTopico(str, PyEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    razao_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200))
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(150))
    telefone: Mapped[str | None] = mapped_column(String(20))
    endereco: Mapped[str | None] = mapped_column(String(300))
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(2))
    cep: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[StatusEmpresa] = mapped_column(
        _oracle_enum(StatusEmpresa, 20), default=StatusEmpresa.ATIVA, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="empresa")
    clientes: Mapped[list["Cliente"]] = relationship(back_populates="empresa")
    topicos: Mapped[list["TopicoCRM"]] = relationship(back_populates="empresa")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    empresa_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("empresas.id"), nullable=True
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(
        _oracle_enum(TipoUsuario, 30), default=TipoUsuario.VENDEDOR, nullable=False
    )
    telefone: Mapped[str | None] = mapped_column(String(20))
    cargo: Mapped[str | None] = mapped_column(String(100))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )

    empresa: Mapped["Empresa | None"] = relationship(back_populates="usuarios")
    topicos_criados: Mapped[list["TopicoCRM"]] = relationship(
        back_populates="responsavel", foreign_keys="TopicoCRM.responsavel_id"
    )
    mensagens: Mapped[list["Mensagem"]] = relationship(back_populates="autor")
    tokens_recuperacao: Mapped[list["TokenRecuperacaoSenha"]] = relationship(
        back_populates="usuario"
    )


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    empresa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("empresas.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150))
    telefone: Mapped[str | None] = mapped_column(String(20))
    celular: Mapped[str | None] = mapped_column(String(20))
    cpf_cnpj: Mapped[str | None] = mapped_column(String(18))
    tipo_pessoa: Mapped[str | None] = mapped_column(String(10))  # PF ou PJ
    endereco: Mapped[str | None] = mapped_column(String(300))
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(2))
    cep: Mapped[str | None] = mapped_column(String(10))
    observacoes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StatusCliente] = mapped_column(
        _oracle_enum(StatusCliente, 20), default=StatusCliente.PROSPECTO, nullable=False
    )
    origem: Mapped[str | None] = mapped_column(String(100))  # facebook, google_ads, etc.
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )

    empresa: Mapped["Empresa"] = relationship(back_populates="clientes")
    topicos: Mapped[list["TopicoCRM"]] = relationship(back_populates="cliente")


class TopicoCRM(Base):
    __tablename__ = "topicos_crm"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    empresa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("empresas.id"), nullable=False
    )
    cliente_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clientes.id"), nullable=True
    )
    responsavel_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[StatusTopico] = mapped_column(
        _oracle_enum(StatusTopico, 20), default=StatusTopico.ABERTO, nullable=False
    )
    prioridade: Mapped[PrioridadeTopico] = mapped_column(
        _oracle_enum(PrioridadeTopico, 20), default=PrioridadeTopico.MEDIA, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime)

    empresa: Mapped["Empresa"] = relationship(back_populates="topicos")
    cliente: Mapped["Cliente | None"] = relationship(back_populates="topicos")
    responsavel: Mapped["Usuario | None"] = relationship(
        back_populates="topicos_criados", foreign_keys=[responsavel_id]
    )
    mensagens: Mapped[list["Mensagem"]] = relationship(
        back_populates="topico", cascade="all, delete-orphan"
    )


class Mensagem(Base):
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topico_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topicos_crm.id"), nullable=False
    )
    autor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="texto")  # texto, nota, sistema
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )

    topico: Mapped["TopicoCRM"] = relationship(back_populates="mensagens")
    autor: Mapped["Usuario"] = relationship(back_populates="mensagens")


class TokenRecuperacaoSenha(Base):
    __tablename__ = "tokens_recuperacao_senha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="tokens_recuperacao")
