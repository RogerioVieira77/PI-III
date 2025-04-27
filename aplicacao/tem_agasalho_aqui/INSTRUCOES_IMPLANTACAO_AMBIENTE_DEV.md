# Instruções de Implantação do Website Agasalho Aqui

## Pré-Requisitos ##
# Prepare seu ambiente de Desenvolvimento
# Não esqueça de ajustar o PATH e o caminhos dos arquivos no seu Projeto

## Requisitos do Sistema
- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Servidor web (Apache ou Nginx)

## Passos para Implantação

### 1. Configuração do Ambiente

1. Instale as dependências do Python:
   ```
   pip install -r requirements.txt
   ```

2. Renomeie o arquivo `.env.example` para `.env` e configure as variáveis de ambiente:
   ```
   cp .env.example .env
   nano .env
   ```
   
   Atualize as seguintes variáveis:
   - `SECRET_KEY`: Uma chave secreta para o Flask (gere uma chave forte)
   - `MYSQL_HOST`: Endereço do servidor MySQL
   - `MYSQL_USER`: Usuário do MySQL
   - `MYSQL_PASSWORD`: Senha do MySQL
   - `MYSQL_DB`: Nome do banco de dados (padrão: agasalho_aqui)
   - `GOOGLE_MAPS_API_KEY`: Sua chave da API do Google Maps

### 2. Configuração do Banco de Dados

1. Crie o banco de dados e as tabelas necessárias:
   ```
   python database/init_db.py
   ```

2. Verifique se o banco de dados foi criado corretamente:
   ```
   mysql -u seu_usuario -p
   USE agasalho_aqui;
   SHOW TABLES;
   ```

### 3. Teste da Aplicação

1. Execute a aplicação em modo de desenvolvimento:
   ```
   python app.py
   ```

2. Acesse http://localhost:5000 no navegador para verificar se a aplicação está funcionando.

3. Execute os testes automatizados (em outro terminal):
   ```
   python test_website.py
   ```

### 4. Implantação em Produção

### Se preferir use o arquivo: INSTRUCOES_IMPLANTACAO_AMBIENTE_PROD para um passo a passo mais detalhado

#### Opção 1: Usando Gunicorn (recomendado)

1. Instale o Gunicorn (já incluído em requirements.txt)
   ```
   pip install gunicorn
   ```

2. Execute a aplicação com Gunicorn:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

#### Opção 2: Usando Apache com mod_wsgi

1. Instale o mod_wsgi:
   ```
   apt-get install libapache2-mod-wsgi-py3
   ```

2. Crie um arquivo WSGI:
   ```
   nano /var/www/agasalho_aqui/wsgi.py
   ```

   Conteúdo do arquivo:
   ```python
   import sys
   import os
   
   # Adicionar diretório da aplicação ao path
   sys.path.insert(0, '/var/www/agasalho_aqui')
   
   # Carregar variáveis de ambiente
   from dotenv import load_dotenv
   load_dotenv('/var/www/agasalho_aqui/.env')
   
   # Importar a aplicação Flask
   from app import app as application
   ```

3. Configure o Apache:
   ```
   nano /etc/apache2/sites-available/agasalho_aqui.conf
   ```

   Conteúdo do arquivo:
   ```
   <VirtualHost *:80>
       ServerName seu_dominio.com
       ServerAdmin webmaster@seu_dominio.com
       
       WSGIDaemonProcess agasalho_aqui python-home=/path/to/venv python-path=/var/www/agasalho_aqui
       WSGIProcessGroup agasalho_aqui
       WSGIScriptAlias / /var/www/agasalho_aqui/wsgi.py
       
       <Directory /var/www/agasalho_aqui>
           Require all granted
       </Directory>
       
       ErrorLog ${APACHE_LOG_DIR}/agasalho_aqui_error.log
       CustomLog ${APACHE_LOG_DIR}/agasalho_aqui_access.log combined
   </VirtualHost>
   ```

4. Ative o site e reinicie o Apache:
   ```
   a2ensite agasalho_aqui.conf
   systemctl restart apache2
   ```

### 5. Configuração de Segurança

1. Certifique-se de que o arquivo `.env` não está acessível publicamente.

2. Configure HTTPS usando Let's Encrypt:
   ```
   apt-get install certbot python3-certbot-apache
   certbot --apache -d seu_dominio.com
   ```

3. Configure um firewall:
   ```
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

### 6. Manutenção

1. Backup regular do banco de dados:
   ```
   mysqldump -u seu_usuario -p agasalho_aqui > backup_$(date +%Y%m%d).sql
   ```

2. Monitoramento de logs:
   ```
   tail -f /var/log/apache2/agasalho_aqui_error.log
   ```

3. Atualização da aplicação:
   - Faça backup dos arquivos e banco de dados
   - Substitua os arquivos da aplicação
   - Reinicie o servidor web
   ```
   systemctl restart apache2
   ```

## Informações de Acesso

- URL do site: http://seu_dominio.com
- Área administrativa: http://seu_dominio.com/administracao
- Usuário administrador padrão: contatoagasalhoaqui@gmail.com
- Senha padrão: admin123 (altere imediatamente após o primeiro login)

## Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento:
- Email: contatoagasalhoaqui@gmail.com
- Telefone: (11) 4002-0922
