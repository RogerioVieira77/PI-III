#ferramenta para teste de email

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging básico para o console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_test')

# Verificar variáveis de ambiente
logger.info("Verificando configurações de e-mail:")
logger.info(f"EMAIL_NOTIFICATION: {os.getenv('EMAIL_NOTIFICATION')}")
logger.info(f"EMAIL_SENDER: {os.getenv('EMAIL_SENDER')}")
logger.info(f"EMAIL_SMTP_SERVER: {os.getenv('EMAIL_SMTP_SERVER')}")
logger.info(f"EMAIL_SMTP_PORT: {os.getenv('EMAIL_SMTP_PORT')}")
logger.info(f"EMAIL_PASSWORD está definido: {'Sim' if os.getenv('EMAIL_PASSWORD') else 'NÃO'}")

# Função de teste de envio de e-mail
def test_email_connection():
    try:
        # Configurações
        smtp_server = os.getenv('EMAIL_SMTP_SERVER')
        smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        sender_email = os.getenv('EMAIL_SENDER')
        password = os.getenv('EMAIL_PASSWORD')
        to_email = os.getenv('EMAIL_NOTIFICATION')

        # Verificar se todas as configurações necessárias estão presentes
        if not all([smtp_server, sender_email, password, to_email]):
            logger.error("Configurações de e-mail incompletas")
            return False

        # Tentar conectar ao servidor SMTP
        logger.info(f"Conectando ao servidor {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Habilitar saída de debug detalhada
        
        # Iniciar TLS
        logger.info("Iniciando TLS...")
        server.starttls()
        
        # Fazer login
        logger.info(f"Fazendo login como {sender_email}...")
        server.login(sender_email, password)
        
        # Criar mensagem
        logger.info("Criando mensagem de teste...")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "E-mail de teste do sistema Agasalho Aqui"
        body = "Este é um e-mail de teste para verificar a configuração SMTP."
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar e-mail
        logger.info(f"Enviando e-mail para {to_email}...")
        server.sendmail(sender_email, to_email, msg.as_string())
        
        # Encerrar conexão
        logger.info("Encerrando conexão...")
        server.quit()
        
        logger.info("E-mail de teste enviado com sucesso!")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao testar conexão de e-mail: {str(e)}", exc_info=True)
        return False

# Executar teste
if __name__ == "__main__":
    test_email_connection()