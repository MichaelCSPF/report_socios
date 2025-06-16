# email_sender.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header # <-- IMPORTANTE: Importar a classe Header
from dotenv import load_dotenv

def read_recipients_from_file(filepath: str) -> list:
    """Lê uma lista de e-mails de um arquivo de texto, separados por vírgula."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            recipients = [email.strip() for email in content.split(',')]
            return [email for email in recipients if email]
    except FileNotFoundError:
        print(f"Erro: O arquivo de destinatários '{filepath}' não foi encontrado.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo de destinatários: {e}")
        return []

def send_email(subject: str, html_body: str, recipients: list):
    """Envia um e-mail com conteúdo HTML para uma lista de destinatários."""
    load_dotenv(dotenv_path='config/.env')

    sender_email = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('EMAIL_HOST')
    smtp_port = os.getenv('EMAIL_PORT')

    if not all([sender_email, password, smtp_server, smtp_port]):
        print("Erro: As configurações de e-mail não estão completas no arquivo .env.")
        return False
    if not recipients:
        print("Nenhum destinatário fornecido. O e-mail não será enviado.")
        return False

    msg = MIMEMultipart('alternative')
    # --- CORREÇÃO APLICADA AQUI ---
    # Usamos a classe Header para garantir a codificação correta do assunto
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)

    part = MIMEText(html_body, 'html', 'utf-8') # Adicionamos o charset aqui também
    msg.attach(part)

    try:
        print(f"Conectando ao servidor SMTP {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            print("Logando no servidor de e-mail...")
            server.login(sender_email, password)
            print("Enviando e-mail...")
            server.sendmail(sender_email, recipients, msg.as_string())
            print(f"E-mail enviado com sucesso para: {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Erro de autenticação. Verifique seu e-mail e senha (ou senha de app).")
        return False
    except Exception as e:
        print(f"Falha ao enviar o e-mail: {e}")
        return False