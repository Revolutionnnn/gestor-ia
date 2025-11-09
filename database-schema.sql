# Esquema de Base de Datos - PostgreSQL

## Tabla: products

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]',
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    description TEXT,
    category VARCHAR(300),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_products_stock ON products(stock);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_keywords ON products USING GIN (keywords);

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
INSERT INTO products (name, keywords, stock, description, category) VALUES
('Laptop Dell', '["laptop", "dell", "intel"]'::jsonb, 50, 'Laptop profesional', 'Electrónica > Laptops'),
('Mouse Logitech', '["mouse", "inalámbrico", "negro"]'::jsonb, 25, 'Mouse inalámbrico', 'Electrónica > Accesorios'),
('Teclado Mecánico', '["teclado", "mecánico", "rgb"]'::jsonb, 15, 'Teclado gaming', 'Electrónica > Periféricos');
```

## Queries Útiles

```sql
-- Productos con stock bajo
SELECT id, name, stock FROM products WHERE stock < 10 ORDER BY stock ASC;

-- Buscar por keyword
SELECT id, name, keywords FROM products WHERE keywords @> '["laptop"]'::jsonb;

-- Resumen de stock
SELECT COUNT(*) AS total, SUM(stock) AS inventario_total FROM products;

-- Productos sin categoría
SELECT id, name FROM products WHERE category IS NULL OR category = '';
```

```

---

**Versión**: 1.0.0 | **Última actualización**: 2025-11-08
