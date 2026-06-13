import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TipoUsuario, Usuario
from app.utils.security import decodificar_token

security_scheme = HTTPBearer()


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    payload = decodificar_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    return usuario


def verificar_tipo_usuario(*tipos_permitidos: TipoUsuario):
    def dependencia(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.tipo not in tipos_permitidos and usuario.tipo != TipoUsuario.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta operação",
            )
        return usuario

    return dependencia


def verificar_empresa(usuario: Usuario, empresa_id: int) -> None:
    if usuario.tipo == TipoUsuario.SUPER_ADMIN:
        return
    if usuario.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a dados de outra empresa",
        )


def gerar_token_recuperacao() -> str:
    return secrets.token_urlsafe(48)


def token_expira_em(horas: int = 2) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=horas)
