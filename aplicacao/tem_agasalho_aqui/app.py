from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import timedelta
import mysql.connector
import os
import requests
import re
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from logging.handlers import RotatingFileHandler
import os

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuração da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave_secreta_temporaria')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'agasalho_aqui')
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY', '')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_PERMANENT'] = False
app.config['EMAIL_NOTIFICATION'] = os.getenv('EMAIL_NOTIFICATION', 'contato@agasalhoaqui.com.br')
app.config['EMAIL_SENDER'] = os.getenv('EMAIL_SENDER', 'sistema@agasalhoaqui.com.br')
app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD', '')
app.config['EMAIL_SMTP_SERVER'] = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
app.config['EMAIL_SMTP_PORT'] = os.getenv('EMAIL_SMTP_PORT', '587')

# Configuração de logs
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Logger para email
email_logger = logging.getLogger('email_logger')
email_logger.setLevel(logging.DEBUG)

# Arquivo de log para e-mails
email_handler = RotatingFileHandler(
    os.path.join(log_dir, 'email.log'),
    maxBytes=1024*1024,  # 1MB
    backupCount=10
)
email_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] - %(message)s'
))
email_logger.addHandler(email_handler)

# Console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
email_logger.addHandler(console)

#Função de envio de email
def send_email(subject, message, to_email):
    """
    Envia um e-mail usando o servidor SMTP configurado.
    """
    # Configurações de e-mail
    sender_email = app.config['EMAIL_SENDER']
    password = app.config['EMAIL_PASSWORD']
    smtp_server = app.config['EMAIL_SMTP_SERVER']
    smtp_port = int(app.config['EMAIL_SMTP_PORT'])
    
    # Validar configurações
    if not password:
        email_logger.error("Senha de e-mail não configurada no .env")
        return False
        
    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Adicionar corpo da mensagem
    msg.attach(MIMEText(message, 'html'))
    
    try:
        email_logger.info(f"Iniciando envio de e-mail para {to_email}")
        email_logger.debug(f"Conectando ao servidor SMTP: {smtp_server}:{smtp_port}")
        
        # Conectar ao servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Criptografar a conexão
        
        email_logger.debug(f"Fazendo login no servidor SMTP com usuário {sender_email}")
        server.login(sender_email, password)
        
        # Enviar e-mail
        text = msg.as_string()
        email_logger.debug(f"Enviando e-mail de {sender_email} para {to_email}")
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        email_logger.info(f"E-mail enviado com sucesso para {to_email}")
        return True
    except Exception as e:
        email_logger.error(f"Erro ao enviar e-mail: {str(e)}", exc_info=True)
        return False

"""Função para Injetar as variáveis em todos os templates"""
@app.context_processor
def inject_user_status():
    return {'is_logged_in': 'user_id' in session}

@app.context_processor
def inject_google_maps_api_key():
    return {'google_maps_api_key': app.config['GOOGLE_MAPS_API_KEY']}

# Função para conectar ao banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )


# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas para as páginas principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/pontosdecoleta')
def pontos_coleta():
    return render_template('pontosdecoleta.html', google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/administracao')
def admin_login():
    if 'user_id' in session:
        return redirect(url_for('logado'))
    return render_template('administracao.html')

@app.route('/logado')
@login_required
def logado():
    return render_template('logado.html')

@app.route('/registroponto')
@login_required
def registroponto():
    return render_template('registroponto.html', google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/termos')
def termos():
    return render_template('termos.html')

@app.route('/privacidade')
def privacidade():
    return render_template('privacidade.html')

# API para buscar pontos de coleta por CEP
@app.route('/api/pontos-coleta', methods=['GET'])
def api_pontos_coleta():
    try:
        cep = request.args.get('cep', '')
        if not cep:
            return jsonify({'error': 'CEP não fornecido'}), 400
        
        # Remover caracteres não numéricos do CEP
        cep = re.sub(r'\D', '', cep)
        
        # Validar CEP
        if len(cep) != 8:
            return jsonify({'error': 'Formato de CEP inválido'}), 400
            
        # Consultar API externa para obter coordenadas do CEP
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao consultar CEP'}), 500
            
        address_data = response.json()
        if 'erro' in address_data:
            return jsonify({'error': 'CEP não encontrado'}), 404
            
        # Obter coordenadas usando Google Maps Geocoding API
        city = address_data.get('localidade', '')
        state = address_data.get('uf', '')
        street = address_data.get('logradouro', '')
        full_address = f'{street}, {city}, {state}, {cep}, Brasil'
        
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={app.config['GOOGLE_MAPS_API_KEY']}"
        geocode_response = requests.get(geocode_url)
        geocode_data = geocode_response.json()
        
        if geocode_data['status'] != 'OK':
            return jsonify({'error': 'Erro ao obter coordenadas para o CEP'}), 500
            
        location = geocode_data['results'][0]['geometry']['location']
        latitude = float(location['lat'])  # Convertendo explicitamente para float
        longitude = float(location['lng'])  # Convertendo explicitamente para float
        
        # Consultar pontos de coleta próximos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar pontos em um raio de aproximadamente 5km
        query = """
        SELECT *, 
            (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) AS distance 
        FROM collection_points 
        WHERE is_active = 1
        HAVING distance < 5 
        ORDER BY distance 
        LIMIT 10
        """
        
        cursor.execute(query, (latitude, longitude, latitude))
        points_raw = cursor.fetchall()
        
        # Converter valores Decimal para float no JSON
        points = []
        for point in points_raw:
            point_dict = dict(point)
            # Converter valores Decimal para float
            point_dict['latitude'] = float(point_dict['latitude'])
            point_dict['longitude'] = float(point_dict['longitude']) 
            point_dict['distance'] = float(point_dict['distance'])
            points.append(point_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'address': full_address
            },
            'points': points
        })
        
    except Exception as e:
        # Adicionar log para depuração
        print(f"Erro na API pontos-coleta: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# API para enviar solicitação de cadastro
@app.route('/api/solicitar-cadastro', methods=['POST'])
def api_solicitar_cadastro():
    try:
        data = request.form
        
        # Log para depuração
        print("Dados recebidos do formulário:")
        for key, value in data.items():
            print(f"- {key}: {value}")
        
        nome = data.get('nome')
        cep = data.get('cep')
        endereco = data.get('endereco')
        numero = data.get('numero')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        uf = data.get('uf')
        email = data.get('email')
        telefone = data.get('telefone')
        horario = data.get('horario')
        site = data.get('site', '')
        
        # Log dos campos principais
        print(f"Campos extraídos: nome='{nome}', endereco='{endereco}', email='{email}', telefone='{telefone}', horario='{horario}'")
        
        # Combinar informações de endereço
        endereco_completo = f"{endereco}, {numero} - {bairro}, {cidade}/{uf}, CEP {cep}"
        
        # Verificação individual de campos obrigatórios
        campos_faltando = []
        if not nome: campos_faltando.append("nome")
        if not endereco: campos_faltando.append("endereco")
        if not email: campos_faltando.append("email")
        if not telefone: campos_faltando.append("telefone")
        if not horario: campos_faltando.append("horario")
        
        if campos_faltando:
            print(f"Campos obrigatórios faltando: {', '.join(campos_faltando)}")
            return jsonify({'error': f'Campos obrigatórios faltando: {", ".join(campos_faltando)}'}), 400
        
        # Inserir solicitação no banco de dados        
        nome = data.get('nome')
        cep = data.get('cep')
        endereco = data.get('endereco')
        numero = data.get('numero')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        uf = data.get('uf')
        email = data.get('email')
        telefone = data.get('telefone')
        horario = data.get('horario')
        site = data.get('site', '')
        
        # Combinar informações de endereço
        endereco_completo = f"{endereco}, {numero} - {bairro}, {cidade}/{uf}, CEP {cep}"
        
        # Validar campos obrigatórios
        if not all([nome, endereco, email, telefone, horario]):
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos'}), 400
        
        # Inserir solicitação no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO registration_requests 
        (name, address, email, phone, opening_hours, website) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (nome, endereco_completo, email, telefone, horario, site))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Preparar e enviar e-mail de notificação
        email_destino = app.config['EMAIL_NOTIFICATION']
        assunto = f"Nova solicitação de cadastro: {nome}"
        
        email_logger.info(f"Preparando e-mail para notificação de novo cadastro de {nome}")
        
        # Criar conteúdo do e-mail com formatação HTML
        mensagem = f"""
        <html>
        <body>
            <h2>Nova solicitação de cadastro de ponto de coleta</h2>
            <p><strong>Nome da instituição:</strong> {nome}</p>
            <p><strong>Endereço completo:</strong> {endereco_completo}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Telefone:</strong> {telefone}</p>
            <p><strong>Horário de funcionamento:</strong> {horario}</p>
            <p><strong>Website:</strong> {site or 'Não informado'}</p>
            <hr>
            <p>Este e-mail foi enviado automaticamente pelo sistema Tem Agasalho Aqui.</p>
        </body>
        </html>
        """
        
        # Enviar e-mail
        email_enviado = send_email(assunto, mensagem, email_destino)
        if not email_enviado:
            email_logger.warning("Falha ao enviar e-mail de notificação, mas o cadastro foi salvo no banco")
        
        return jsonify({'success': True, 'message': 'Solicitação enviada com sucesso'})
        
    except Exception as e:
        email_logger.error(f"Erro ao processar solicitação: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    

#Api para administração de usuários

@app.route('/addadmuser')
@login_required
def add_admin_user():
        return render_template('addadmuser.html')


@app.route('/api/admin/cadastrar', methods=['POST'])
@login_required
def api_admin_cadastrar():
    try:
        print("Recebeu requisição para cadastro de administrador")
        # Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Dados recebidos: nome={name}, email={email}, senha={'*'*len(password)}")
        
        # Validar dados
        if not name or not email or not password:
            print("Dados inválidos: campos obrigatórios faltando")
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
            
        # Verificar se o email já está em uso
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"Email {email} já está em uso")
            cursor.close()
            conn.close()
            return jsonify({'error': 'Este email já está em uso'}), 400
            
        # Gerar hash da senha
        password_hash = generate_password_hash(password)
        
        # Inserir usuário no banco de dados
        try:
            print("Tentando inserir no banco de dados")
            cursor.execute(
                "INSERT INTO admin_users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            conn.commit()
            print("Usuário inserido com sucesso!")
        except Exception as db_error:
            print(f"Erro ao inserir no banco: {str(db_error)}")
            raise db_error
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Administrador cadastrado com sucesso'})
        
    except Exception as e:
        print(f"Erro ao cadastrar administrador: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para registrar novo ponto de coleta (área administrativa)
@app.route('/api/admin/registrar-ponto', methods=['POST'])
@login_required
def api_registrar_ponto():
    try:
        # Extrair dados do formulário
        nome = request.form.get('nome')
        apelido = request.form.get('apelido')
        cnpj = request.form.get('cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        cep = request.form.get('cep')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        site = request.form.get('site', '')
        funcionamento = request.form.get('funcionamento')
        observacoes = request.form.get('observacoes', '')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Validar campos obrigatórios
        if not all([nome, apelido, cnpj, telefone, email, cep, endereco, cidade, estado, funcionamento, latitude, longitude]):
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos'}), 400
        
        # Converter latitude e longitude para float
        try:
            lat_float = float(latitude)
            lng_float = float(longitude)
        except ValueError:
            return jsonify({'error': 'Coordenadas geográficas inválidas'}), 400
            
        # Inserir no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO collection_points 
        (name, nickname, address, postal_code, city, state, latitude, longitude, cnpj, phone, email, website, opening_hours, observations) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            nome, apelido, endereco, cep, cidade, estado, lat_float, lng_float, 
            cnpj, telefone, email, site, funcionamento, observacoes
        ))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Ponto de coleta registrado com sucesso'})
        
    except Exception as e:
        print(f"Erro ao registrar ponto de coleta: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para alterar senha de administrador
@app.route('/alteraradm')
@login_required
def alterar_admin():
    return render_template('alteraradm.html')

@app.route('/api/admin/alterar-senha', methods=['POST'])
@login_required
def api_admin_alterar_senha():
    try:
        print("Recebeu requisição para alteração de senha de administrador")
        # Obter dados do formulário
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        # Validar dados
        if not email or not new_password:
            print("Dados inválidos: campos obrigatórios faltando")
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
            
        # Verificar se o email existe no banco
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Email {email} não encontrado")
            cursor.close()
            conn.close()
            return jsonify({'error': 'Administrador não encontrado com este email'}), 404
            
        # Gerar hash da nova senha
        password_hash = generate_password_hash(new_password)
        
        # Atualizar senha no banco de dados
        try:
            print(f"Atualizando senha para o usuário com email {email}")
            cursor.execute(
                "UPDATE admin_users SET password = %s WHERE email = %s",
                (password_hash, email)
            )
            conn.commit()
            print("Senha atualizada com sucesso!")
        except Exception as db_error:
            print(f"Erro ao atualizar senha no banco: {str(db_error)}")
            raise db_error
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso'})
        
    except Exception as e:
        print(f"Erro ao alterar senha: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API para login administrativo
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validar dados
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
            
        # Verificar no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin_users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Verificar se o usuário existe e a senha está correta
        if user and check_password_hash(user['password'], password):
            # Criar sessão
            session.permanent = True  # Marcando a sessão como permanente para usar o PERMANENT_SESSION_LIFETIME
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            
            return jsonify({
                'success': True,
                'redirect': url_for('logado')
            })
        else:
            return jsonify({'error': 'Email ou senha inválidos'}), 401
            
    except Exception as e:
        print(f"Erro de login: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Rota para logout
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


