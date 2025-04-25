import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Conectar ao banco de dados usando informações do .env
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)
cursor = conn.cursor(dictionary=True)

# Verificar se o usuário existe
email = 'adm_test@example.com'
cursor.execute("SELECT * FROM admin_users WHERE email = %s", (email,))
user = cursor.fetchone()

if user:
    print(f"O usuário {email} já existe no banco de dados.")
    # Atualizar a senha do usuário
    password_hash = generate_password_hash('Mudar123@')
    cursor.execute("UPDATE admin_users SET password = %s WHERE email = %s", 
                  (password_hash, email))
    conn.commit()
    print(f"Senha do usuário {email} atualizada com sucesso.")
else:
    print(f"O usuário {email} não existe no banco de dados.")
    # Inserir novo usuário
    password_hash = generate_password_hash('Mudar123@')
    cursor.execute("INSERT INTO admin_users (name, email, password) VALUES (%s, %s, %s)",
                  ('adm_test', email, password_hash))
    conn.commit()
    print(f"Novo usuário {email} criado com sucesso.")

# Exibir usuário para confirmação
cursor.execute("SELECT id, name, email FROM admin_users WHERE email = %s", (email,))
user = cursor.fetchone()
print(f"Usuário confirmado no banco: ID={user['id']}, Nome={user['name']}, Email={user['email']}")

cursor.close()
conn.close()