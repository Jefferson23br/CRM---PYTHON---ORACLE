from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Empresa, TipoUsuario, Usuario
from app.schemas import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    PaginatedResponse,
)
from app.utils.dependencies import get_usuario_atual, verificar_empresa, verificar_tipo_usuario

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("", response_model=PaginatedResponse[EmpresaResponse])
def listar_empresas(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.SUPER_ADMIN)
    ),
):
    query = db.query(Empresa)
    total = query.count()
    empresas = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[EmpresaResponse.model_validate(e) for e in empresas],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obter_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    verificar_empresa(usuario, empresa_id)
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    return EmpresaResponse.model_validate(empresa)


@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def criar_empresa(
    dados: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.SUPER_ADMIN)
    ),
):
    if db.query(Empresa).filter(Empresa.cnpj == dados.cnpj).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ já cadastrado")

    empresa = Empresa(**dados.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return EmpresaResponse.model_validate(empresa)


@router.put("/{empresa_id}", response_model=EmpresaResponse)
def atualizar_empresa(
    empresa_id: int,
    dados: EmpresaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    if usuario.tipo not in (TipoUsuario.SUPER_ADMIN, TipoUsuario.ADMIN_EMPRESA):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")

    verificar_empresa(usuario, empresa_id)
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return EmpresaResponse.model_validate(empresa)


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.SUPER_ADMIN)
    ),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    db.delete(empresa)
    db.commit()
