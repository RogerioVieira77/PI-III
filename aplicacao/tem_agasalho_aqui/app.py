from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
import os
import json
import requests
import re
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
        return redirect(url_for('logado'))
    return render_template('administracao.html')

@app.route('/logado')
@login_required
def logado():
    return render_template('logado.html')

@app.route('/registroponto')
@login_required
def registro_ponto():
    return render_template('registroponto.html')

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
