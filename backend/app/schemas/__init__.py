from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import (
    PrioridadeTopico,
    StatusCliente,
    StatusEmpresa,
    StatusTopico,
    TipoUsuario,
)

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Empresa ---

class EmpresaBase(BaseModel):
    razao_social: str = Field(..., min_length=2, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=300)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = Field(None, min_length=2, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=300)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    status: Optional[StatusEmpresa] = None


class EmpresaResponse(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusEmpresa
    criado_em: datetime
    atualizado_em: Optional[datetime] = None


# --- Usuário ---

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)
    cargo: Optional[str] = Field(None, max_length=100)
    tipo: TipoUsuario = TipoUsuario.VENDEDOR


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8, max_length=100)
    empresa_id: Optional[int] = None


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    telefone: Optional[str] = Field(None, max_length=20)
    cargo: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoUsuario] = None
    ativo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: Optional[int] = None
    ativo: bool
    email_verificado: bool
    ultimo_acesso: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None


# --- Cliente ---

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    tipo_pessoa: Optional[str] = Field(None, max_length=10)
    endereco: Optional[str] = Field(None, max_length=300)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None
    status: StatusCliente = StatusCliente.PROSPECTO
    origem: Optional[str] = Field(None, max_length=100)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    tipo_pessoa: Optional[str] = Field(None, max_length=10)
    endereco: Optional[str] = Field(None, max_length=300)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None
    status: Optional[StatusCliente] = None
    origem: Optional[str] = Field(None, max_length=100)


class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None


# --- Tópico CRM ---

class TopicoBase(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=100)
    status: StatusTopico = StatusTopico.ABERTO
    prioridade: PrioridadeTopico = PrioridadeTopico.MEDIA
    cliente_id: Optional[int] = None
    responsavel_id: Optional[int] = None


class TopicoCreate(TopicoBase):
    pass


class TopicoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=2, max_length=200)
    descricao: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=100)
    status: Optional[StatusTopico] = None
    prioridade: Optional[PrioridadeTopico] = None
    cliente_id: Optional[int] = None
    responsavel_id: Optional[int] = None


class TopicoResponse(TopicoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    fechado_em: Optional[datetime] = None


# --- Mensagem ---

class MensagemBase(BaseModel):
    conteudo: str = Field(..., min_length=1)
    tipo: str = Field(default="texto", max_length=50)


class MensagemCreate(MensagemBase):
    pass


class MensagemUpdate(BaseModel):
    conteudo: Optional[str] = Field(None, min_length=1)
    tipo: Optional[str] = Field(None, max_length=50)


class MensagemResponse(MensagemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topico_id: int
    autor_id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None


# --- Autenticação ---

class RegistroRequest(BaseModel):
    """Registro inicial: cria empresa + admin."""
    empresa: EmpresaCreate
    usuario: UsuarioCreate


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class RecuperarSenhaRequest(BaseModel):
    email: EmailStr


class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=8, max_length=100)


class MensagemResponseGenerica(BaseModel):
    mensagem: str
    sucesso: bool = True
