# Esquema de Base de Datos - PostgreSQL

## Tabla: products

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]',
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    description TEXT,
    category VARCHAR(300),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_products_stock ON products(stock);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_keywords ON products USING GIN (keywords);
CREATE INDEX idx_products_is_active ON products(is_active);

-- Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Datos de Prueba

```sql
INSERT INTO products (name, keywords, stock, description, category, is_active) VALUES
('Laptop Dell XPS 15', '["laptop", "dell", "intel", "profesional"]'::jsonb, 50, 'Laptop profesional de alto rendimiento', 'Electrónica > Laptops', TRUE),
('Mouse Logitech MX Master', '["mouse", "inalámbrico", "negro", "ergonómico"]'::jsonb, 25, 'Mouse inalámbrico ergonómico', 'Electrónica > Accesorios', TRUE),
('Teclado Mecánico RGB', '["teclado", "mecánico", "rgb", "gaming"]'::jsonb, 15, 'Teclado mecánico para gaming', 'Electrónica > Periféricos', TRUE),
('Monitor 4K Samsung', '["monitor", "4k", "samsung", "27 pulgadas"]'::jsonb, 8, 'Monitor 4K profesional', 'Electrónica > Monitores', TRUE),
('Producto Descontinuado', '["legacy", "viejo"]'::jsonb, 0, 'Producto que ya no se vende', 'Varios', FALSE);
```

## Migración para bases de datos existentes

```sql
-- Agregar columna is_active a productos existentes
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Crear índice
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Marcar productos sin stock como inactivos (opcional)
-- UPDATE products SET is_active = FALSE WHERE stock = 0;
```

## Queries Útiles

```sql
-- Productos activos con stock bajo
SELECT id, name, stock FROM products 
WHERE is_active = TRUE AND stock < 10 
ORDER BY stock ASC;

-- Productos activos vs inactivos
SELECT is_active, COUNT(*) AS total, SUM(stock) AS stock_total 
FROM products 
GROUP BY is_active;

-- Buscar por keyword solo en productos activos
SELECT id, name, keywords FROM products 
WHERE is_active = TRUE AND keywords @> '["laptop"]'::jsonb;

-- Resumen de stock de productos activos
SELECT COUNT(*) AS total, SUM(stock) AS inventario_total 
FROM products 
WHERE is_active = TRUE;

-- Productos sin categoría
SELECT id, name FROM products WHERE category IS NULL OR category = '';

-- Activar/Desactivar producto
UPDATE products SET is_active = FALSE WHERE id = 'uuid-del-producto';
UPDATE products SET is_active = TRUE WHERE id = 'uuid-del-producto';
```

```

---

**Versión**: 1.0.0 | **Última actualización**: 2025-11-08
