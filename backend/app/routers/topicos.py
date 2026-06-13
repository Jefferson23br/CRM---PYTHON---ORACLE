from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StatusTopico, TopicoCRM, Usuario
from app.schemas import PaginatedResponse, TopicoCreate, TopicoResponse, TopicoUpdate
from app.utils.dependencies import get_usuario_atual

router = APIRouter(prefix="/topicos", tags=["Tópicos CRM"])


def _empresa_id_obrigatorio(usuario: Usuario) -> int:
    if not usuario.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem empresa vinculada",
        )
    return usuario.empresa_id


@router.get("", response_model=PaginatedResponse[TopicoResponse])
def listar_topicos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filtro: StatusTopico | None = Query(None, alias="status"),
    cliente_id: int | None = Query(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    query = db.query(TopicoCRM).filter(TopicoCRM.empresa_id == empresa_id)

    if status_filtro:
        query = query.filter(TopicoCRM.status == status_filtro)
    if cliente_id:
        query = query.filter(TopicoCRM.cliente_id == cliente_id)

    total = query.count()
    topicos = (
        query.order_by(TopicoCRM.criado_em.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        items=[TopicoResponse.model_validate(t) for t in topicos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{topico_id}", response_model=TopicoResponse)
def obter_topico(
    topico_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    topico = (
        db.query(TopicoCRM)
        .filter(TopicoCRM.id == topico_id, TopicoCRM.empresa_id == empresa_id)
        .first()
    )
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    return TopicoResponse.model_validate(topico)


@router.post("", response_model=TopicoResponse, status_code=status.HTTP_201_CREATED)
def criar_topico(
    dados: TopicoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    topico = TopicoCRM(
        empresa_id=empresa_id,
        responsavel_id=dados.responsavel_id or usuario.id,
        **dados.model_dump(exclude={"responsavel_id"}),
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return TopicoResponse.model_validate(topico)


@router.put("/{topico_id}", response_model=TopicoResponse)
def atualizar_topico(
    topico_id: int,
    dados: TopicoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    topico = (
        db.query(TopicoCRM)
        .filter(TopicoCRM.id == topico_id, TopicoCRM.empresa_id == empresa_id)
        .first()
    )
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")

    dados_dict = dados.model_dump(exclude_unset=True)
    if dados_dict.get("status") in (StatusTopico.RESOLVIDO, StatusTopico.FECHADO):
        topico.fechado_em = datetime.now(timezone.utc)

    for campo, valor in dados_dict.items():
        setattr(topico, campo, valor)

    db.commit()
    db.refresh(topico)
    return TopicoResponse.model_validate(topico)


@router.delete("/{topico_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_topico(
    topico_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    empresa_id = _empresa_id_obrigatorio(usuario)
    topico = (
        db.query(TopicoCRM)
        .filter(TopicoCRM.id == topico_id, TopicoCRM.empresa_id == empresa_id)
        .first()
    )
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")

    db.delete(topico)
    db.commit()
