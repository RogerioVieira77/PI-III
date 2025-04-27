#!/usr/bin/env python3
# Script para criar e inicializar o banco de dados

import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carregar variáveis de ambiente
# Configurações do banco de dados
load_dotenv()
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'agasalho_user'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
}

if not os.getenv('MYSQL_PASSWORD'):
    print("AVISO: Senha do banco de dados não configurada no .env!")

# Nome do banco de dados
db_name = os.getenv('MYSQL_DB', 'agasalho_aqui')

def create_database():
    """Criar o banco de dados se não existir"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Criar banco de dados se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Banco de dados '{db_name}' criado ou já existente.")
        
        # Usar o banco de dados
        cursor.execute(f"USE `{db_name}`")
        
        # Criar tabelas
        create_tables(cursor)
        
        # Inserir dados iniciais
        insert_initial_data(cursor)
        
        # Commit das alterações
        conn.commit()
        
        print("Inicialização do banco de dados concluída com sucesso!")
        
    except mysql.connector.Error as err:
        print(f"Erro: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexão com MySQL fechada.")

def create_tables(cursor):
    # Verificar se existem tabelas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    tables_count = len(tables)
    
    # Perguntar apenas se estamos em produção e já existem tabelas
    if os.getenv('ENVIRONMENT') == 'production' and tables_count > 0:
        confirm = input("ATENÇÃO: Você está em ambiente de produção. "
                    "Deseja recriar as tabelas? (s/N): ")
        if confirm.lower() != 's':
            print("Operação cancelada.")
            return

    """Criar as tabelas do banco de dados"""

    
    
    # Tabela de usuários administrativos

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    print("Tabela 'admin_users' criada ou já existente.")
    
    # Tabela de pontos de coleta
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS collection_points (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL COMMENT 'Razão Social do Parceiro',
        nickname VARCHAR(255) NOT NULL COMMENT 'Nome que aparecerá no site',
        address VARCHAR(255) NOT NULL,
        postal_code VARCHAR(20) NOT NULL,
        city VARCHAR(100) NOT NULL,
        state VARCHAR(50) NOT NULL,
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        cnpj VARCHAR(20),
        phone VARCHAR(20) NOT NULL,
        email VARCHAR(255) NOT NULL,
        website VARCHAR(255),
        opening_hours TEXT NOT NULL,
        observations TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    print("Tabela 'collection_points' criada ou já existente.")
    
    # Tabela de solicitações de cadastro pendentes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registration_requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        opening_hours TEXT NOT NULL,
        website VARCHAR(255),
        status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    print("Tabela 'registration_requests' criada ou já existente.")
    
    # Criar índices para otimizar consultas
    try:
        cursor.execute("CREATE INDEX idx_collection_points_postal_code ON collection_points(postal_code)")
    except mysql.connector.Error as err:
        if err.errno != 1061:  # Error code for duplicate index
            raise
    try:
        cursor.execute("CREATE INDEX idx_collection_points_coordinates ON collection_points(latitude, longitude)")
    except mysql.connector.Error as err:
        if err.errno != 1061:
            raise
    try:
        cursor.execute("CREATE INDEX idx_collection_points_active ON collection_points(is_active)")
    except mysql.connector.Error as err:
        if err.errno != 1061:
            raise
    print("Índices criados ou já existentes.")
    
    # Verificar se a coluna is_active existe e criar se necessário
    cursor.execute("SHOW COLUMNS FROM collection_points LIKE 'is_active'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE collection_points ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Flag que indica se o ponto de coleta está ativo (1) ou inativo (0)'")
        cursor.execute("UPDATE collection_points SET is_active = 1")


def insert_initial_data(cursor):
    """Inserir dados iniciais no banco de dados"""
    
    # Verificar se já existe um usuário administrador
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Inserir usuário administrador padrão
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO admin_users (email, password, name) VALUES (%s, %s, %s)",
            ('contatoagasalhoaqui@gmail.com', admin_password, 'Administrador')
        )
        print("Usuário administrador padrão criado.")
    else:
        print("Usuário administrador já existe.")
    
    # Inserir alguns pontos de coleta de exemplo
    cursor.execute("SELECT COUNT(*) FROM collection_points")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Pontos de coleta de exemplo em São Paulo
        example_points = [
            {
                'name': 'Espaço MIDH',
                'nickname': 'Espaço MIDH',
                'address': 'Rua Augusta, 1500, Consolação, São Paulo, SP',
                'postal_code': '01304-001',
                'city': 'São Paulo',
                'state': 'SP',
                'latitude': -23.5505,
                'longitude': -46.6333,
                'cnpj': '12.345.678/0001-90',
                'phone': '(11) 3456-7890',
                'email': 'contato@espacomidh.org',
                'website': 'https://www.espacomidh.org',
                'opening_hours': 'Segunda a Sexta, 9h às 18h',
                'observations': 'Aceitamos roupas em bom estado para todas as idades.'
            },
            {
                'name': 'Centro de Doações Esperança',
                'nickname': 'Doações Esperança',
                'address': 'Av. Paulista, 1000, Bela Vista, São Paulo, SP',
                'postal_code': '01310-100',
                'city': 'São Paulo',
                'state': 'SP',
                'latitude': -23.5651,
                'longitude': -46.6551,
                'cnpj': '98.765.432/0001-10',
                'phone': '(11) 2345-6789',
                'email': 'contato@doacoesesperanca.org',
                'website': 'https://www.doacoesesperanca.org',
                'opening_hours': 'Segunda a Sábado, 10h às 19h',
                'observations': 'Foco em roupas de inverno e cobertores.'
            },
            {
                'name': 'Associação Amigos Solidários',
                'nickname': 'Amigos Solidários',
                'address': 'Rua Oscar Freire, 500, Jardins, São Paulo, SP',
                'postal_code': '01426-000',
                'city': 'São Paulo',
                'state': 'SP',
                'latitude': -23.5622,
                'longitude': -46.6693,
                'cnpj': '45.678.901/0001-23',
                'phone': '(11) 3333-4444',
                'email': 'contato@amigossolidarios.org',
                'website': 'https://www.amigossolidarios.org',
                'opening_hours': 'Terça a Domingo, 9h às 17h',
                'observations': 'Aceitamos também brinquedos e livros infantis.'
            }
        ]
        
        for point in example_points:
            cursor.execute("""
            INSERT INTO collection_points 
            (name, nickname, address, postal_code, city, state, latitude, longitude, cnpj, phone, email, website, opening_hours, observations) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                point['name'], point['nickname'], point['address'], point['postal_code'], 
                point['city'], point['state'], point['latitude'], point['longitude'], 
                point['cnpj'], point['phone'], point['email'], point['website'], 
                point['opening_hours'], point['observations']
            ))
        
        print("Pontos de coleta de exemplo inseridos.")
    else:
        print("Pontos de coleta já existem.")

if __name__ == "__main__":
    create_database()
