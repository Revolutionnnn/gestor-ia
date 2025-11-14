-- Migración para agregar funcionalidad de productos activos/inactivos
-- y roles de usuario al sistema existente

-- ============================================================================
-- PARTE 1: Actualizar tabla de usuarios con roles
-- ============================================================================

-- Agregar columna role si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users 
        ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user' 
        CHECK (role IN ('user', 'admin'));
        
        RAISE NOTICE 'Columna role agregada a tabla users';
    ELSE
        RAISE NOTICE 'Columna role ya existe en tabla users';
    END IF;
END $$;

-- Crear índice para role
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- PARTE 2: Actualizar tabla de productos con is_active
-- ============================================================================

-- Agregar columna is_active si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE products 
        ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
        
        RAISE NOTICE 'Columna is_active agregada a tabla products';
    ELSE
        RAISE NOTICE 'Columna is_active ya existe en tabla products';
    END IF;
END $$;

-- Crear índice para is_active
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- ============================================================================
-- PARTE 3: Actualizar datos existentes (opcional)
-- ============================================================================

-- Marcar productos sin stock como inactivos (comentado por seguridad)
-- UNCOMMENT si deseas aplicar esta lógica:
-- UPDATE products SET is_active = FALSE WHERE stock = 0;

-- Establecer todos los productos existentes como activos
-- UPDATE products SET is_active = TRUE WHERE is_active IS NULL;

-- ============================================================================
-- PARTE 4: Crear usuario administrador de prueba
-- ============================================================================

-- NOTA: La contraseña debe ser hasheada por el backend antes de insertar
-- Este es solo un ejemplo, NO ejecutar directamente

-- Primero registra un usuario normal desde el backend:
-- POST /auth/register con {"email": "admin@ejemplo.com", "password": "admin123"}

-- Luego actualiza su rol a admin:
-- UPDATE users SET role = 'admin' WHERE email = 'admin@ejemplo.com';

-- ============================================================================
-- PARTE 5: Verificación
-- ============================================================================

-- Verificar estructura de users
SELECT 
    column_name, 
    data_type, 
    column_default, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Verificar estructura de products
SELECT 
    column_name, 
    data_type, 
    column_default, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'products'
ORDER BY ordinal_position;

-- Contar productos por estado
SELECT 
    is_active,
    COUNT(*) as total,
    SUM(stock) as stock_total
FROM products
GROUP BY is_active;

-- Contar usuarios por rol
SELECT 
    role,
    COUNT(*) as total
FROM users
GROUP BY role;

-- ============================================================================
-- ROLLBACK (si necesitas revertir)
-- ============================================================================

-- PRECAUCIÓN: Esto eliminará las columnas y sus datos
-- Solo ejecutar si realmente necesitas revertir la migración

-- DROP INDEX IF EXISTS idx_users_role;
-- ALTER TABLE users DROP COLUMN IF EXISTS role;

-- DROP INDEX IF EXISTS idx_products_is_active;
-- ALTER TABLE products DROP COLUMN IF EXISTS is_active;
