import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

settings = get_settings()


async def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> bool:
    if not settings.smtp_user or not settings.smtp_password:
        return False

    mensagem = MIMEMultipart("alternative")
    mensagem["From"] = settings.smtp_from
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            mensagem,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=settings.smtp_tls,
        )
        return True
    except Exception:
        return False


async def enviar_email_recuperacao_senha(email: str, token: str) -> bool:
    link = f"{settings.frontend_url}/redefinir-senha?token={token}"
    assunto = "CRM Piloto - Recuperação de Senha"
    corpo = f"""
    <html>
    <body>
        <h2>Recuperação de Senha</h2>
        <p>Você solicitou a redefinição da sua senha no CRM Piloto.</p>
        <p>Clique no link abaixo para criar uma nova senha:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Este link expira em 2 horas.</p>
        <p>Se você não solicitou esta alteração, ignore este e-mail.</p>
    </body>
    </html>
    """
    return await enviar_email(email, assunto, corpo)
