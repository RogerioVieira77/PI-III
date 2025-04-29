## Este guia foi desenvolvido especificamente para hospedar a aplicação em VPS

# Requisitos e Tecnologias

## Linguagens:

- BackEnd
    - Python 3.12.3
    - Flask

- FrontEnd
    - HTML
    - CSS
    - Java Script

# Banco
    - MySQL 5.7 ou superior

# Servidor
    - Ubuntu 24.04
    - NGIX (Http Server/Proxy Reverso)
    - Hospedado em um VPS na Hostinger

# Funcionalidades

## As instruções consideram que já existe um servidor e uma conexão SSH configurada.

```bash

 ## 1. Preparação Inicial do Servidor

 Acesse seu VPS da Hostinger

Logo através de um console utilizando: 
    ssh usuario@seu-ip-da-hostinger

```bash
# Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências essenciais
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential
sudo apt install -y git curl wget nano

# Instalar MySQL
sudo apt install -y mysql-server mysql-client libmysqlclient-dev

# Instalar Nginx
sudo apt install -y nginx

# Instalar Certbot para SSL (opcional)
sudo apt install -y certbot python3-certbot-nginx
```

## 2. Configuração do MySQL

```bash
# Configurar segurança do MySQL
sudo mysql_secure_installation

# Acessar o MySQL
sudo mysql

# Dentro do MySQL, criar banco e usuário
CREATE DATABASE agasalho_aqui CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agasalho_user'@'localhost' IDENTIFIED BY 'SUA_SENHA_SEGURA';
GRANT ALL PRIVILEGES ON agasalho_aqui.* TO 'agasalho_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. Configuração da Estrutura de Diretórios

```bash
# Criar diretórios necessários
sudo mkdir -p /var/www/agasalho_aqui
sudo chown -R $USER:$USER /var/www/agasalho_aqui

# Clonar o repositório
cd /var/www/agasalho_aqui
git clone https://github.com/RogerioVieira77/PI-III.git aplicacao
```

## 4. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual na pasta principal do projeto
cd /var/www/agasalho_aqui
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r aplicacao/tem_agasalho_aqui/requirements.txt
pip install gunicorn
```

## 5. Configuração do Arquivo WSGI

```bash
# Criar/verificar arquivo wsgi.py no diretório da aplicação
cd /var/www/agasalho_aqui/aplicacao/tem_agasalho_aqui
cat > wsgi.py << 'EOF'
import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar a aplicação Flask
from app import app

if __name__ == "__main__":
    app.run()
EOF
```

## 6. Configuração das Variáveis de Ambiente

```bash
# Criar/modificar arquivo .env no diretório da aplicação
cd /var/www/agasalho_aqui/aplicacao/tem_agasalho_aqui
cat > .env << 'EOF'
SECRET_KEY=chave_secreta_muito_segura_e_longa_aqui
MYSQL_HOST=localhost
MYSQL_USER=agasalho_user
MYSQL_PASSWORD=SUA_SENHA_SEGURA
MYSQL_DB=agasalho_aqui
GOOGLE_MAPS_API_KEY=sua_chave_api_google_maps
EMAIL_NOTIFICATION=seu-email-destino@exemplo.com
EMAIL_SENDER=sistema@seudominio.com
EMAIL_PASSWORD=senha_do_email
EMAIL_SMTP_SERVER=smtp.seuservidoremail.com
EMAIL_SMTP_PORT=587
ENVIRONMENT=production
EOF

# Ajustar permissões
chmod 600 .env
```

## 7. Inicialização do Banco de Dados

```bash
# Ativar ambiente virtual caso não esteja ativo
cd /var/www/agasalho_aqui
source venv/bin/activate

# Inicializar o banco de dados
cd aplicacao/tem_agasalho_aqui
python database/init_db.py
```

## 8. Criação de Diretório de Logs

```bash
# Criar diretório de logs
sudo mkdir -p /var/log/agasalho_aqui
sudo chown -R $USER:www-data /var/log/agasalho_aqui
```

## 9. Configuração do Supervisor para Gerenciar Gunicorn

```bash
# Instalar supervisor
sudo apt install -y supervisor

# Criar arquivo de configuração do supervisor
sudo nano /etc/supervisor/conf.d/agasalho_aqui.conf
```

Conteúdo do arquivo:

```ini
[program:agasalho_aqui]
directory=/var/www/agasalho_aqui/aplicacao/tem_agasalho_aqui
command=/var/www/agasalho_aqui/venv/bin/gunicorn --workers=3 --bind=127.0.0.1:8000 wsgi:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/agasalho_aqui/gunicorn.err.log
stdout_logfile=/var/log/agasalho_aqui/gunicorn.out.log
environment=
    LANG=en_US.UTF-8,
    LC_ALL=en_US.UTF-8,
    LC_LANG=en_US.UTF-8,
    PATH="/var/www/agasalho_aqui/venv/bin"
```

## 10. Configuração do Nginx como Proxy Reverso

```bash
# Criar arquivo de configuração do site
sudo nano /etc/nginx/sites-available/agasalho_aqui
```

Conteúdo do arquivo:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /static {
        alias /var/www/agasalho_aqui/aplicacao/tem_agasalho_aqui/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 11. Ativação do Site e Reinício dos Serviços

```bash
# Ativar o site
sudo ln -s /etc/nginx/sites-available/agasalho_aqui /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuração do Nginx
sudo nginx -t

# Aplicar permissões corretas para os arquivos da aplicação
sudo chown -R www-data:www-data /var/www/agasalho_aqui

# Reiniciar serviços
sudo systemctl restart supervisor
sudo systemctl restart nginx
```

## 12. Configuração de SSL com Certbot (recomendado)

```bash
# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com
```

## 13. Verificação Final

```bash
# Verificar status do supervisor
sudo supervisorctl status agasalho_aqui

# Verificar logs
tail -f /var/log/agasalho_aqui/gunicorn.err.log

# Verificar se a aplicação está acessível
curl -I http://localhost:8000
```

## 14. Solução de Problemas Comuns

### Se o Gunicorn não iniciar:

```bash
# Verificar manualmente
cd /var/www/agasalho_aqui
source venv/bin/activate
cd aplicacao/tem_agasalho_aqui
gunicorn --bind=127.0.0.1:8000 wsgi:app
```

### Se as permissões de arquivos derem problemas:

```bash
# Corrigir permissões
sudo find /var/www/agasalho_aqui -type d -exec chmod 755 {} \;
sudo find /var/www/agasalho_aqui -type f -exec chmod 644 {} \;
sudo chown -R www-data:www-data /var/www/agasalho_aqui
```

### Se o MySQL apresentar problemas de autenticação:

```bash
# Corrigir autenticação
sudo mysql
ALTER USER 'agasalho_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'SUA_SENHA_SEGURA';
FLUSH PRIVILEGES;
```

# Verificar logs
(venv) root@srv728514:/etc/nginx/sites-enabled# tail -f /var/log/agasalho_aqui/gunicorn.err.log

## 15. Ativação do Site e Reinício dos Serviços

Agora que sua aplicação está funcionando internamente, você deve verificar:

1. **Acesso externo**: Tente acessar seu site pelo domínio configurado
2. **SSL**: Se configurou o Certbot, verifique se o HTTPS está funcionando
3. **Backups**: Configure backups regulares do banco de dados

```bash
# Verificar se Nginx está redirecionando corretamente
sudo nginx -t
sudo systemctl status nginx

# Testar acesso pelo domínio (em outro terminal/máquina)
curl -I https://seu-dominio.com
```

## 16 Ajuste a Configuração do Nginx para acesso via IP

Edite o arquivo de configuração do Nginx:

```bash
sudo nano /etc/nginx/sites-available/agasalho_aqui
```

Modifique a linha `server_name` para incluir o IP:

```nginx
server {
    listen 80;
    server_name 82.25.75.88;  # Adicionado o IP do servidor

    # Resto da configuração permanece igual...
}
```

# Reinicie o Nginx

```bash
sudo nginx -t        # Verificar se a configuração está correta
sudo systemctl reload nginx
```

# Acesse pelo IP

Você pode acessar o site usando:

```
http://82.25.75.88
```

Se você configurou SSL com Certbot, o acesso seguro seria:

```
https://82.25.75.88
```

No entanto, como não há um domínio associado, você verá um aviso de segurança no navegador ao usar HTTPS sem um domínio registrado.

## 4. Considerações de Segurança

- Este método é bom para testes temporários
- Quando estiver pronto para produção, registre um domínio e configure o SSL corretamente
- Considere limitar o acesso por IP usando um firewall como o UFW se o site não estiver pronto para acesso público

```bash
# Opcional: restringir acesso apenas ao seu IP
sudo apt install ufw
sudo ufw allow from seu_ip_pessoal to any port 80,443
sudo ufw allow ssh
sudo ufw enable
```

# Testar acesso pelo IP ou Domínio (em outro terminal/máquina)

curl -I https://seu-dominio.com
curl -I https://ip-do-servidor