-- Esquema do banco de dados para o projeto "Agasalho Aqui"

-- Tabela de usuários administrativos
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de pontos de coleta
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
);

-- Tabela de solicitações de cadastro pendentes
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
);

-- Índices para otimizar consultas geográficas
CREATE INDEX idx_collection_points_postal_code ON collection_points(postal_code);
CREATE INDEX idx_collection_points_coordinates ON collection_points(latitude, longitude);
CREATE INDEX idx_collection_points_active ON collection_points(is_active);

-- Inserir um usuário administrativo padrão (senha: admin123)
-- Em produção, esta senha deve ser alterada imediatamente
INSERT INTO admin_users (email, password, name) 
VALUES ('contatoagasalhoaqui@gmail.com', '$2b$12$1oE8Cv8Bp.Y3XPgdRUkVvuHLJ/XZVA0t7hkCwqfO9B2VDq/R1U6Ue', 'Administrador');
