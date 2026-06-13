from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Empresa,
    StatusEmpresa,
    TipoUsuario,
    TokenRecuperacaoSenha,
    Usuario,
)
from app.schemas import (
    LoginRequest,
    MensagemResponseGenerica,
    RecuperarSenhaRequest,
    RedefinirSenhaRequest,
    RegistroRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.services.email import enviar_email_recuperacao_senha
from app.utils.dependencies import (
    gerar_token_recuperacao,
    get_usuario_atual,
    token_expira_em,
)
from app.utils.security import (
    criar_access_token,
    criar_refresh_token,
    hash_senha,
    verificar_senha,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def registrar(dados: RegistroRequest, db: Session = Depends(get_db)):
    """Registra nova empresa e usuário administrador."""
    if db.query(Empresa).filter(Empresa.cnpj == dados.empresa.cnpj).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado",
        )

    if db.query(Usuario).filter(Usuario.email == dados.usuario.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )

    empresa = Empresa(**dados.empresa.model_dump(), status=StatusEmpresa.ATIVA)
    db.add(empresa)
    db.flush()

    usuario = Usuario(
        empresa_id=empresa.id,
        nome=dados.usuario.nome,
        email=dados.usuario.email,
        senha_hash=hash_senha(dados.usuario.senha),
        tipo=TipoUsuario.ADMIN_EMPRESA,
        telefone=dados.usuario.telefone,
        cargo=dados.usuario.cargo or "Administrador",
        ativo=True,
        email_verificado=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token_data = {"sub": str(usuario.id), "empresa_id": empresa.id}
    return TokenResponse(
        access_token=criar_access_token(token_data),
        refresh_token=criar_refresh_token(token_data),
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    usuario.ultimo_acesso = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)

    token_data = {"sub": str(usuario.id), "empresa_id": usuario.empresa_id}
    return TokenResponse(
        access_token=criar_access_token(token_data),
        refresh_token=criar_refresh_token(token_data),
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioResponse)
def obter_usuario_atual(usuario: Usuario = Depends(get_usuario_atual)):
    return UsuarioResponse.model_validate(usuario)


@router.post("/recuperar-senha", response_model=MensagemResponseGenerica)
async def recuperar_senha(dados: RecuperarSenhaRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if usuario:
        token_valor = gerar_token_recuperacao()
        token = TokenRecuperacaoSenha(
            usuario_id=usuario.id,
            token=token_valor,
            expira_em=token_expira_em(2),
        )
        db.add(token)
        db.commit()
        await enviar_email_recuperacao_senha(usuario.email, token_valor)

    return MensagemResponseGenerica(
        mensagem="Se o e-mail estiver cadastrado, você receberá instruções de recuperação.",
    )


@router.post("/redefinir-senha", response_model=MensagemResponseGenerica)
def redefinir_senha(dados: RedefinirSenhaRequest, db: Session = Depends(get_db)):
    token = (
        db.query(TokenRecuperacaoSenha)
        .filter(
            TokenRecuperacaoSenha.token == dados.token,
            TokenRecuperacaoSenha.usado == False,  # noqa: E712
            TokenRecuperacaoSenha.expira_em > datetime.now(timezone.utc),
        )
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    usuario = db.query(Usuario).filter(Usuario.id == token.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    usuario.senha_hash = hash_senha(dados.nova_senha)
    token.usado = True
    db.commit()

    return MensagemResponseGenerica(mensagem="Senha redefinida com sucesso.")
