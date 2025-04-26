## Passo a passo para publicação da Aplicação em um VPS

## Como exemplo foi usado um VPS no HOSTINGER.

### 1. Acesse seu VPS da Hostinger

```bash
ssh usuario@seu-ip-da-hostinger
```

### 2. Instale as dependências no servidor

```bash
# Atualizar repositórios
sudo apt update
sudo apt upgrade -y

# Instalar Python e ferramentas necessárias
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y mysql-server libmysqlclient-dev
sudo apt install -y nginx supervisor

# Instalar dependências para SSL
sudo apt install -y certbot python3-certbot-nginx
```

### 3. Configure o MySQL

```bash
# Configurar MySQL (siga os prompts para definir a senha do root)
sudo mysql_secure_installation

# Acessar o MySQL
sudo mysql

# Dentro do MySQL, crie o banco de dados e o usuário
CREATE DATABASE agasalho_aqui;
CREATE USER 'agasalho_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON agasalho_aqui.* TO 'agasalho_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Configure o diretório da aplicação

```bash
# Criar diretório para a aplicação
sudo mkdir -p /var/www/agasalho_aqui
sudo chown $USER:$USER /var/www/agasalho_aqui

# Clonar ou transferir os arquivos do projeto para o servidor
# Opção 1: Clonar de um repositório Git (se disponível)
cd /var/www/
git clone https://github.com/seu-usuario/tem_agasalho_aqui.git agasalho_aqui

# Opção 2: Transferir arquivos via SCP
# (Execute isso em seu computador local, não no servidor)
# scp -r ./tem_agasalho_aqui/* usuario@seu-ip-da-hostinger:/var/www/agasalho_aqui/
```

### 5. Configurar ambiente virtual e instalar dependências

```bash
cd /var/www/agasalho_aqui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Se não estiver no requirements.txt
```

### 6. Configurar variáveis de ambiente

```bash
# Criar arquivo .env
cp .env.example .env  # Se você tiver um arquivo de exemplo
nano .env

# Configure as variáveis no arquivo .env:
SECRET_KEY=uma_chave_secreta_longa_e_aleatoria
MYSQL_HOST=localhost
MYSQL_USER=agasalho_user
MYSQL_PASSWORD=sua_senha_segura
MYSQL_DB=agasalho_aqui
GOOGLE_MAPS_API_KEY=sua_chave_api_google_maps
EMAIL_NOTIFICATION=seu-email@dominio.com
EMAIL_SENDER=sistema@seudominio.com
EMAIL_PASSWORD=sua_senha_de_email
EMAIL_SMTP_SERVER=smtp.seuservidoremail.com
EMAIL_SMTP_PORT=587
```

### 7. Inicializar o banco de dados

```bash
source venv/bin/activate
python database/init_db.py
```

### 8. Configurar Gunicorn como serviço via Supervisor

```bash
sudo nano /etc/supervisor/conf.d/agasalho_aqui.conf
```

Conteúdo:
```
[program:agasalho_aqui]
directory=/var/www/agasalho_aqui
command=/var/www/agasalho_aqui/venv/bin/gunicorn wsgi:app -w 4 -b 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/agasalho_aqui/gunicorn.err.log
stdout_logfile=/var/log/agasalho_aqui/gunicorn.out.log
```

Criar diretório de logs e aplicar permissões:
```bash
sudo mkdir -p /var/log/agasalho_aqui
sudo chown -R www-data:www-data /var/log/agasalho_aqui
sudo chown -R www-data:www-data /var/www/agasalho_aqui
```

### 9. Configurar Nginx como proxy reverso

```bash
sudo nano /etc/nginx/sites-available/agasalho_aqui
```

Conteúdo:
```
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /var/www/agasalho_aqui/static;
    }
}
```

Ativar o site e reiniciar Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/agasalho_aqui /etc/nginx/sites-enabled
sudo nginx -t  # Testar a configuração
sudo systemctl restart nginx
```

### 10. Iniciar a aplicação

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start agasalho_aqui
```

### 11. Configurar HTTPS com Certbot

```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
# Siga as instruções na tela
```

### 12. Configurar Firewall (opcional, dependendo das configurações da Hostinger)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

### 13. Verificação final

1. Acesse seu site em `https://seu-dominio.com`
2. Verifique os logs para problemas:
   ```bash
   sudo tail -f /var/log/agasalho_aqui/gunicorn.err.log
   ```

## Manutenção e Operação

### Backup do banco de dados

```bash
# Criar um script de backup
sudo nano /etc/cron.daily/backup-agasalho-aqui
```

Conteúdo:
```bash
#!/bin/bash
DATE=$(date +"%Y%m%d")
BACKUP_DIR="/var/backups/agasalho_aqui"
mkdir -p $BACKUP_DIR
mysqldump -u agasalho_user -p'sua_senha_segura' agasalho_aqui > $BACKUP_DIR/agasalho_aqui_$DATE.sql
```

Tornar executável:
```bash
sudo chmod +x /etc/cron.daily/backup-agasalho-aqui
```

### Atualizando a aplicação

```bash
cd /var/www/agasalho_aqui
git pull  # Se você usou Git
source venv/bin/activate
pip install -r requirements.txt  # Se houver novas dependências
sudo supervisorctl restart agasalho_aqui
```

### Monitoramento

Para monitorar a aplicação:
```bash
sudo supervisorctl status agasalho_aqui
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/agasalho_aqui/gunicorn.err.log
```

Com essas configurações, sua aplicação Tem Agasalho Aqui estará funcionando em produção na Hostinger VPS de forma segura e escalável.