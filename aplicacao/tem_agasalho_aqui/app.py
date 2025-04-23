from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
import os
import json
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

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
        return redirect(url_for('admin_dashboard'))
    return render_template('administracao.html')

@app.route('/registroponto')
@login_required
def registro_ponto():
    return render_template('registroponto.html')

# API para buscar pontos de coleta por CEP
@app.route('/api/pontos-coleta', methods=['GET'])
def api_pontos_coleta():
    cep = request.args.get('cep', '')
    
    if not cep:
        return jsonify({'error': 'CEP não fornecido'}), 400
    
    # Buscar coordenadas do CEP usando API externa (ViaCEP + Nominatim)
    try:
        # Primeiro, obter o endereço completo do CEP
        via_cep_url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(via_cep_url)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao consultar o CEP'}), 500
        
        cep_data = response.json()
        
        if 'erro' in cep_data:
            return jsonify({'error': 'CEP não encontrado'}), 404
        
        # Montar o endereço completo para buscar as coordenadas
        endereco = f"{cep_data['logradouro']}, {cep_data['bairro']}, {cep_data['localidade']}, {cep_data['uf']}, Brasil"
        
        # Buscar coordenadas usando Nominatim (OpenStreetMap)
        nominatim_url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': endereco,
            'format': 'json',
            'limit': 1
        }
        
        headers = {
            'User-Agent': 'AgasalhoAqui/1.0'
        }
        
        geo_response = requests.get(nominatim_url, params=params, headers=headers)
        
        if geo_response.status_code != 200 or not geo_response.json():
            return jsonify({'error': 'Não foi possível obter as coordenadas do CEP'}), 500
        
        location_data = geo_response.json()[0]
        latitude = float(location_data['lat'])
        longitude = float(location_data['lon'])
        
        # Buscar pontos de coleta próximos no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consulta usando a fórmula de Haversine para calcular distância
        query = """
        SELECT *, 
            (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) AS distance 
        FROM collection_points 
        WHERE is_active = TRUE 
        ORDER BY distance 
        LIMIT 5
        """
        
        cursor.execute(query, (latitude, longitude, latitude))
        pontos_coleta = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'cep': cep,
            'latitude': latitude,
            'longitude': longitude,
            'pontos_coleta': pontos_coleta
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para enviar solicitação de cadastro
@app.route('/api/solicitar-cadastro', methods=['POST'])
def api_solicitar_cadastro():
    try:
        data = request.form
        
        nome = data.get('nome')
        endereco = data.get('endereco')
        email = data.get('email')
        telefone = data.get('telefone')
        horario = data.get('horario')
        site = data.get('site', '')
        
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
        
        cursor.execute(query, (nome, endereco, email, telefone, horario, site))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Enviar e-mail de notificação (simulado)
        # Em uma implementação real, usaríamos uma biblioteca como smtplib
        print(f"E-mail enviado para contatoagasalhoaqui@gmail.com: Nova solicitação de cadastro de {nome}")
        
        return jsonify({'success': True, 'message': 'Solicitação enviada com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para autenticação de administradores
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'error': 'E-mail e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM admin_users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'E-mail ou senha inválidos'}), 401
        
        # Armazenar informações do usuário na sessão
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        
        return jsonify({'success': True, 'redirect': url_for('registro_ponto')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para registrar novo ponto de coleta (área administrativa)
@app.route('/api/admin/registrar-ponto', methods=['POST'])
@login_required
def api_registrar_ponto():
    try:
        data = request.form
        
        nome = data.get('nome')
        apelido = data.get('apelido')
        endereco = data.get('endereco')
        cnpj = data.get('cnpj')
        telefone = data.get('telefone')
        site = data.get('site', '')
        observacoes = data.get('observacoes', '')
        
        # Validar campos obrigatórios
        if not all([nome, apelido, endereco, cnpj, telefone]):
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos'}), 400
        
        # Obter coordenadas do endereço usando Nominatim
        try:
            nominatim_url = 'https://nominatim.openstreetmap.org/search'
            params = {
                'q': endereco,
                'format': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'AgasalhoAqui/1.0'
            }
            
            geo_response = requests.get(nominatim_url, params=params, headers=headers)
            
            if geo_response.status_code != 200 or not geo_response.json():
                return jsonify({'error': 'Não foi possível obter as coordenadas do endereço'}), 500
            
            location_data = geo_response.json()[0]
            latitude = float(location_data['lat'])
            longitude = float(location_data['lon'])
            
            # Extrair informações de cidade e estado do resultado
            address_parts = location_data.get('display_name', '').split(', ')
            city = address_parts[-3] if len(address_parts) >= 3 else ''
            state = address_parts[-2] if len(address_parts) >= 2 else ''
            postal_code = ''
            
            # Tentar extrair CEP do endereço
            for part in address_parts:
                if part.replace('-', '').isdigit() and len(part.replace('-', '')) == 8:
                    postal_code = part
                    break
            
        except Exception as e:
            return jsonify({'error': f'Erro ao geocodificar endereço: {str(e)}'}), 500
        
        # Inserir ponto de coleta no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO collection_points 
        (name, nickname, address, postal_code, city, state, latitude, longitude, cnpj, phone, email, website, opening_hours, observations) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            nome, apelido, endereco, postal_code, city, state, latitude, longitude, 
            cnpj, telefone, 'contato@' + site.replace('https://', '').replace('http://', '') if site else '', 
            site, 'Segunda a Sexta, 9h às 18h', observacoes
        ))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Ponto de coleta registrado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para logout
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
