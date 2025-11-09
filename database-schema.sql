# Esquema de Base de Datos - PostgreSQL

## 📊 Tabla Principal: products

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla principal de productos
CREATE TABLE products (
    -- Identificador único
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Información básica del producto
    name VARCHAR(200) NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]',
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    
    -- Campos generados por IA
    description TEXT,
    category VARCHAR(300),
    
    -- Metadatos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX idx_products_stock ON products(stock);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_keywords ON products USING GIN (keywords);

-- Comentarios para documentación
COMMENT ON TABLE products IS 'Catálogo de productos con enriquecimiento IA';
COMMENT ON COLUMN products.id IS 'UUID v4 generado automáticamente';
COMMENT ON COLUMN products.name IS 'Nombre comercial del producto (3-200 chars)';
COMMENT ON COLUMN products.keywords IS 'Array JSON de palabras clave descriptivas';
COMMENT ON COLUMN products.stock IS 'Cantidad actual en inventario (no negativo)';
COMMENT ON COLUMN products.description IS 'Descripción generada por LLM';
COMMENT ON COLUMN products.category IS 'Categoría jerárquica (e.g., Ropa > Hombre > Camisetas)';
```

## 📋 Tabla Auxiliar: stock_alerts (Opcional - Para auditoría)

```sql
CREATE TABLE stock_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    stock_level INTEGER NOT NULL,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    webhook_sent BOOLEAN DEFAULT FALSE,
    webhook_response TEXT,
    
    CONSTRAINT fk_product
        FOREIGN KEY (product_id) 
        REFERENCES products(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_stock_alerts_product ON stock_alerts(product_id);
CREATE INDEX idx_stock_alerts_triggered ON stock_alerts(triggered_at DESC);

COMMENT ON TABLE stock_alerts IS 'Registro de alertas de stock bajo para auditoría';
COMMENT ON COLUMN stock_alerts.stock_level IS 'Nivel de stock cuando se disparó la alerta';
COMMENT ON COLUMN stock_alerts.webhook_sent IS 'Indica si el webhook a n8n fue exitoso';
```

## 🔄 Trigger: Actualizar updated_at automáticamente

```sql
-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger en products
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column() IS 'Actualiza automáticamente el campo updated_at';
```

## 🌱 Datos de Prueba (Seeds)

```sql
-- Insertar productos de ejemplo para testing
INSERT INTO products (name, keywords, stock, description, category) VALUES
(
    'Camiseta Algodón Premium',
    '["rojo", "algodón", "verano", "casual", "manga corta"]'::jsonb,
    50,
    'Camiseta de algodón 100% premium en vibrante color rojo, perfecta para el verano. Diseño casual y cómodo con manga corta, ideal para cualquier ocasión informal. Tejido suave que permite la transpiración.',
    'Ropa > Hombre > Camisetas'
),
(
    'Audífonos Bluetooth Noise-Cancelling',
    '["negro", "inalámbrico", "noise-cancelling", "bluetooth", "premium"]'::jsonb,
    15,
    'Audífonos premium con tecnología de cancelación activa de ruido. Batería de larga duración (30 horas), conexión Bluetooth 5.0 y sonido Hi-Fi. Perfectos para viajeros y amantes de la música.',
    'Electrónica > Audio > Audífonos'
),
(
    'Smartwatch Deportivo GPS',
    '["GPS", "resistente al agua", "monitor cardíaco", "batería 7 días", "negro"]'::jsonb,
    8,
    'Smartwatch deportivo de última generación con GPS integrado y resistencia al agua IP68. Monitorea tu ritmo cardíaco 24/7 y disfruta de hasta 7 días de batería. Ideal para atletas.',
    'Electrónica > Wearables > Smartwatches'
),
(
    'Cafetera Express Italiana',
    '["acero inoxidable", "6 tazas", "italiana", "cocina", "plateado"]'::jsonb,
    25,
    'Cafetera express tradicional italiana en acero inoxidable de alta calidad. Capacidad para 6 tazas de espresso perfecto. Apta para todo tipo de cocinas incluyendo inducción. Elegante diseño atemporal.',
    'Hogar > Cocina > Cafeteras'
),
(
    'Mochila Laptop 17" Impermeable',
    '["negro", "impermeable", "laptop", "17 pulgadas", "viaje", "USB"]'::jsonb,
    30,
    'Mochila profesional con compartimento acolchado para laptop de hasta 17". Material impermeable, puerto USB para carga, múltiples bolsillos organizadores. Perfecta para viajes de negocios.',
    'Accesorios > Mochilas > Laptop'
);

-- Verificar inserción
SELECT id, name, stock, category FROM products;
```

## 📊 Vistas Útiles

```sql
-- Vista: Productos con stock bajo
CREATE OR REPLACE VIEW low_stock_products AS
SELECT 
    id,
    name,
    stock,
    category,
    created_at,
    CASE 
        WHEN stock = 0 THEN 'OUT_OF_STOCK'
        WHEN stock < 5 THEN 'CRITICAL'
        WHEN stock < 10 THEN 'LOW'
    END AS stock_status
FROM products
WHERE stock < 10
ORDER BY stock ASC, name;

COMMENT ON VIEW low_stock_products IS 'Productos con stock bajo para alertas';

-- Vista: Resumen por categoría
CREATE OR REPLACE VIEW products_by_category AS
SELECT 
    category,
    COUNT(*) AS total_products,
    SUM(stock) AS total_stock,
    AVG(stock) AS avg_stock,
    MIN(stock) AS min_stock,
    MAX(stock) AS max_stock
FROM products
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_products DESC;

COMMENT ON VIEW products_by_category IS 'Estadísticas de productos agrupados por categoría';
```

## 🔍 Queries Útiles

```sql
-- 1. Buscar productos por keyword
SELECT id, name, keywords, stock
FROM products
WHERE keywords @> '["bluetooth"]'::jsonb;

-- 2. Productos añadidos en las últimas 24 horas
SELECT id, name, created_at, stock
FROM products
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- 3. Productos más vendidos (requiere tabla de ventas)
-- Para el PoC: Productos con menor stock (asumiendo que empezaron igual)
SELECT id, name, stock, category
FROM products
ORDER BY stock ASC
LIMIT 10;

-- 4. Buscar productos sin categoría (falló la IA)
SELECT id, name, keywords, description
FROM products
WHERE category IS NULL OR category = '';

-- 5. Total de productos e inventario
SELECT 
    COUNT(*) AS total_productos,
    SUM(stock) AS inventario_total,
    COUNT(CASE WHEN stock < 10 THEN 1 END) AS productos_stock_bajo
FROM products;
```

## 🔐 Roles y Permisos (Producción)

```sql
-- Crear usuario de aplicación (no usar superuser en producción)
CREATE USER app_backend WITH PASSWORD 'your_secure_password_here';

-- Permisos limitados
GRANT CONNECT ON DATABASE ecommerce_db TO app_backend;
GRANT USAGE ON SCHEMA public TO app_backend;
GRANT SELECT, INSERT, UPDATE ON products TO app_backend;
GRANT SELECT, INSERT ON stock_alerts TO app_backend;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_backend;

-- Usuario read-only para reportes
CREATE USER app_readonly WITH PASSWORD 'readonly_password_here';
GRANT CONNECT ON DATABASE ecommerce_db TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
```

## 🧪 Testing del Schema

```sql
-- Test 1: Insertar producto válido
BEGIN;
INSERT INTO products (name, keywords, stock)
VALUES ('Test Product', '["test", "keyword"]'::jsonb, 100)
RETURNING *;
ROLLBACK;

-- Test 2: Validar constraint de stock (debe fallar)
BEGIN;
INSERT INTO products (name, keywords, stock)
VALUES ('Invalid Product', '["test"]'::jsonb, -5);  -- ❌ Debe fallar
ROLLBACK;

-- Test 3: Actualizar stock y verificar updated_at
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = (SELECT id FROM products LIMIT 1)
RETURNING id, stock, created_at, updated_at;
-- updated_at debe ser diferente de created_at
ROLLBACK;

-- Test 4: Búsqueda por keywords
SELECT name FROM products WHERE keywords @> '["rojo"]'::jsonb;

-- Test 5: Trigger de stock alert (si se implementa)
BEGIN;
UPDATE products SET stock = 5 WHERE name = 'Test Product';
SELECT * FROM stock_alerts WHERE product_id = (SELECT id FROM products WHERE name = 'Test Product');
ROLLBACK;
```

## 📈 Migrations con Alembic (Python)

### Archivo: `alembic/versions/001_initial_schema.py`

```python
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Habilitar extensión uuid-ossp
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Crear tabla products
    op.create_table(
        'products',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, 
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('keywords', JSONB, nullable=False, server_default="'[]'"),
        sa.Column('stock', sa.Integer, nullable=False, server_default='0'),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(300)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('stock >= 0', name='check_stock_non_negative')
    )
    
    # Crear índices
    op.create_index('idx_products_stock', 'products', ['stock'])
    op.create_index('idx_products_category', 'products', ['category'])
    op.create_index('idx_products_created_at', 'products', ['created_at'], 
                    postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_products_keywords', 'products', ['keywords'], 
                    postgresql_using='gin')
    
    # Crear función de trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Crear trigger
    op.execute("""
        CREATE TRIGGER update_products_updated_at
            BEFORE UPDATE ON products
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    op.drop_table('products')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE')
```

## 🎯 Consideraciones de Performance

### Índices Recomendados

| Índice | Tipo | Uso |
|--------|------|-----|
| `idx_products_stock` | B-tree | Queries de stock bajo (`WHERE stock < 10`) |
| `idx_products_category` | B-tree | Filtrado por categoría |
| `idx_products_created_at` | B-tree DESC | Listar productos recientes |
| `idx_products_keywords` | GIN | Búsquedas JSON (`WHERE keywords @> ...`) |

### Estimación de Tamaño

```
Tamaño estimado por registro:
- UUID: 16 bytes
- name (avg 50 chars): 50 bytes
- keywords (avg 5 items): 150 bytes
- stock: 4 bytes
- description (avg 200 chars): 200 bytes
- category (avg 50 chars): 50 bytes
- timestamps: 16 bytes
Total: ~486 bytes por producto

Para 100,000 productos: ~48 MB
Para 1,000,000 productos: ~480 MB
```

### Optimizaciones

1. **Particionamiento** (si > 1M productos):
```sql
CREATE TABLE products_2025_11 PARTITION OF products
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

2. **Vacuum automático**:
```sql
ALTER TABLE products SET (autovacuum_vacuum_scale_factor = 0.1);
```

3. **Materialized View** para estadísticas:
```sql
CREATE MATERIALIZED VIEW products_stats AS
SELECT category, COUNT(*), SUM(stock)
FROM products
GROUP BY category;

-- Refresh periódico
REFRESH MATERIALIZED VIEW CONCURRENTLY products_stats;
```

---

**Última actualización**: 2025-11-08  
**Versión del Schema**: 1.0.0  
**Compatible con**: PostgreSQL 14+
