from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cliente, Usuario
from app.schemas import ClienteCreate, ClienteResponse, ClienteUpdate, PaginatedResponse
from app.utils.dependencies import get_usuario_atual, verificar_empresa

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def _empresa_id_obrigatorio(usuario: Usuario) -> int:
    if not usuario.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem empresa vinculada",
        )
    return usuario.empresa_id


@router.get("", response_model=PaginatedResponse[ClienteResponse])
def listar_clientes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    busca: str | None = Query(None, description="Busca por nome, e-mail ou telefone"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    query = db.query(Cliente).filter(Cliente.empresa_id == empresa_id)

    if busca:
        termo = f"%{busca.lower()}%"
        query = query.filter(
            or_(
                func.lower(Cliente.nome).like(termo),
                func.lower(Cliente.email).like(termo),
                Cliente.telefone.like(termo),
                Cliente.celular.like(termo),
            )
        )

    total = query.count()
    clientes = query.order_by(Cliente.nome).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[ClienteResponse.model_validate(c) for c in clientes],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id, Cliente.empresa_id == empresa_id)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return ClienteResponse.model_validate(cliente)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    dados: ClienteCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    cliente = Cliente(empresa_id=empresa_id, **dados.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int,
    dados: ClienteUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id, Cliente.empresa_id == empresa_id)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id, Cliente.empresa_id == empresa_id)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    db.delete(cliente)
    db.commit()
