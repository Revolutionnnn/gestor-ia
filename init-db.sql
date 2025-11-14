-- Esquema de Base de Datos - PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (LOWER(email));
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]',
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    price INTEGER NOT NULL DEFAULT 0 CHECK (price >= 0),
    description TEXT,
    category VARCHAR(300),
    image_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para products
CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_keywords ON products USING GIN (keywords);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para products
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Usuario administrador inicial
-- Email: admin@pruebas.com
-- Password: pruebas-2025
-- Hash generado con bcrypt
INSERT INTO users (email, full_name, hashed_password, role) VALUES
('admin@pruebas.com', 'Administrador', '$2b$12$aGvMAie14.Da643hrPDfu.fA9MzmXaphMidl3WZZwnAZCXw/.efsK', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Datos de prueba
INSERT INTO products (name, keywords, stock, price, description, category, image_url, is_active) VALUES
('Laptop Dell XPS 15', '["laptop", "dell", "intel", "profesional"]'::jsonb, 50, 1299, 'Laptop profesional de alto rendimiento', 'Electrónica', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500', TRUE),
('Mouse Logitech MX Master', '["mouse", "inalámbrico", "negro", "ergonómico"]'::jsonb, 25, 99, 'Mouse inalámbrico ergonómico', 'Accesorios', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500', TRUE),
('Teclado Mecánico RGB', '["teclado", "mecánico", "rgb", "gaming"]'::jsonb, 15, 149, 'Teclado mecánico para gaming', 'Periféricos', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500', TRUE),
('Monitor 4K Samsung', '["monitor", "4k", "samsung", "27 pulgadas"]'::jsonb, 8, 599, 'Monitor 4K profesional', 'Monitores', 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500', TRUE),
('Auriculares Sony WH-1000XM4', '["auriculares", "sony", "noise cancelling", "bluetooth"]'::jsonb, 30, 349, 'Auriculares premium con cancelación de ruido', 'Audio', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500', TRUE),
('Webcam Logitech C920', '["webcam", "logitech", "1080p", "streaming"]'::jsonb, 20, 79, 'Webcam Full HD para videoconferencias', 'Accesorios', 'https://images.unsplash.com/photo-1584931429105-e6b53f3d0d60?w=500', TRUE),
('Producto Descontinuado', '["legacy", "viejo"]'::jsonb, 0, 0, 'Producto que ya no se vende', 'Varios', NULL, FALSE)
ON CONFLICT DO NOTHING;
