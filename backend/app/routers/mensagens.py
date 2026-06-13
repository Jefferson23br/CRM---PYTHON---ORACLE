from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mensagem, TopicoCRM, Usuario
from app.schemas import MensagemCreate, MensagemResponse, MensagemUpdate, PaginatedResponse
from app.utils.dependencies import get_usuario_atual

router = APIRouter(prefix="/topicos/{topico_id}/mensagens", tags=["Mensagens"])


def _validar_topico_empresa(db: Session, topico_id: int, usuario: Usuario) -> TopicoCRM:
    if not usuario.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem empresa vinculada",
        )
    topico = (
        db.query(TopicoCRM)
        .filter(TopicoCRM.id == topico_id, TopicoCRM.empresa_id == usuario.empresa_id)
        .first()
    )
    if not topico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tópico não encontrado")
    return topico


@router.get("", response_model=PaginatedResponse[MensagemResponse])
def listar_mensagens(
    topico_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _validar_topico_empresa(db, topico_id, usuario)
    query = db.query(Mensagem).filter(Mensagem.topico_id == topico_id)
    total = query.count()
    mensagens = (
        query.order_by(Mensagem.criado_em.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        items=[MensagemResponse.model_validate(m) for m in mensagens],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.post("", response_model=MensagemResponse, status_code=status.HTTP_201_CREATED)
def criar_mensagem(
    topico_id: int,
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _validar_topico_empresa(db, topico_id, usuario)
    mensagem = Mensagem(
        topico_id=topico_id,
        autor_id=usuario.id,
        conteudo=dados.conteudo,
        tipo=dados.tipo,
    )
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)
    return MensagemResponse.model_validate(mensagem)


@router.put("/{mensagem_id}", response_model=MensagemResponse)
def atualizar_mensagem(
    topico_id: int,
    mensagem_id: int,
    dados: MensagemUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _validar_topico_empresa(db, topico_id, usuario)
    mensagem = (
        db.query(Mensagem)
        .filter(Mensagem.id == mensagem_id, Mensagem.topico_id == topico_id)
        .first()
    )
    if not mensagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada")

    if mensagem.autor_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o autor pode editar a mensagem",
        )

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(mensagem, campo, valor)

    db.commit()
    db.refresh(mensagem)
    return MensagemResponse.model_validate(mensagem)


@router.delete("/{mensagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_mensagem(
    topico_id: int,
    mensagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _validar_topico_empresa(db, topico_id, usuario)
    mensagem = (
        db.query(Mensagem)
        .filter(Mensagem.id == mensagem_id, Mensagem.topico_id == topico_id)
        .first()
    )
    if not mensagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada")

    if mensagem.autor_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o autor pode excluir a mensagem",
        )

    db.delete(mensagem)
    db.commit()
