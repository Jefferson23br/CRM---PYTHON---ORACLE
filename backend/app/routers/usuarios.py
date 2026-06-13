from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TipoUsuario, Usuario
from app.schemas import PaginatedResponse, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.utils.dependencies import get_usuario_atual, verificar_empresa, verificar_tipo_usuario
from app.utils.security import hash_senha

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def _empresa_id_usuario(usuario: Usuario, empresa_id: int | None) -> int:
    if usuario.tipo == TipoUsuario.SUPER_ADMIN:
        if not empresa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="empresa_id é obrigatório para super admin",
            )
        return empresa_id
    if not usuario.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem empresa vinculada",
        )
    return usuario.empresa_id


@router.get("", response_model=PaginatedResponse[UsuarioResponse])
def listar_usuarios(
    empresa_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.ADMIN_EMPRESA, TipoUsuario.GERENTE)
    ),
):
    eid = _empresa_id_usuario(usuario, empresa_id)
    verificar_empresa(usuario, eid)

    query = db.query(Usuario).filter(Usuario.empresa_id == eid)
    total = query.count()
    usuarios = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[UsuarioResponse.model_validate(u) for u in usuarios],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if alvo.empresa_id:
        verificar_empresa(usuario_atual, alvo.empresa_id)

    return UsuarioResponse.model_validate(alvo)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.ADMIN_EMPRESA, TipoUsuario.GERENTE)
    ),
):
    empresa_id = dados.empresa_id or _empresa_id_usuario(usuario, dados.empresa_id)
    verificar_empresa(usuario, empresa_id)

    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    novo = Usuario(
        empresa_id=empresa_id,
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        tipo=dados.tipo,
        telefone=dados.telefone,
        cargo=dados.cargo,
        ativo=True,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return UsuarioResponse.model_validate(novo)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.ADMIN_EMPRESA, TipoUsuario.GERENTE)
    ),
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if alvo.empresa_id:
        verificar_empresa(usuario_atual, alvo.empresa_id)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(alvo, campo, valor)

    db.commit()
    db.refresh(alvo)
    return UsuarioResponse.model_validate(alvo)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(
        verificar_tipo_usuario(TipoUsuario.ADMIN_EMPRESA)
    ),
):
    alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if alvo.empresa_id:
        verificar_empresa(usuario_atual, alvo.empresa_id)

    db.delete(alvo)
    db.commit()
