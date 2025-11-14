# Backend Principal - Sistema de Gestión de Productos con IA

Backend principal del sistema de e-commerce con integración de microservicios de IA, autenticación y alertas.

## 🚀 Características

- **Gestión de productos con IA**: Generación automática de descripciones y categorías
- **Sistema de autenticación**: Integración con microservicio de auth (JWT)
- **Control de acceso basado en roles**: Admin vs Usuario público
- **Productos activos/inactivos**: Control de visibilidad en catálogo
- **Alertas de stock bajo**: Notificaciones automáticas vía webhook
- **API RESTful**: Documentación OpenAPI/Swagger

## 📋 Rutas de la API

### Productos - Endpoints Públicos (sin autenticación)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/products` | Lista productos activos |
| `GET` | `/products/{id}` | Detalle de producto activo |

### Productos - Usuario Autenticado

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---------------|
| `POST` | `/products/{id}/sell` | Vender producto | Token JWT |

### Productos - Solo Administrador

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---------------|
| `GET` | `/products/admin/all` | Lista todos los productos | Admin JWT |
| `GET` | `/products/admin/{id}` | Ver cualquier producto | Admin JWT |
| `POST` | `/products` | Crear producto | Admin JWT |
| `PUT` | `/products/{id}` | Actualizar producto | Admin JWT |
| `DELETE` | `/products/{id}` | Eliminar producto | Admin JWT |

### Salud

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del servicio |

## 🔐 Autenticación

El backend se integra con el **microservicio-auth** para validar tokens JWT.

### Headers requeridos para rutas protegidas

```http
Authorization: Bearer <token_jwt>
```

### Flujo de autenticación

1. Usuario hace login en el microservicio de auth (`POST /auth/login`)
2. Recibe un token JWT
3. Incluye el token en el header `Authorization` de las peticiones
4. Backend valida el token con el microservicio de auth
5. Si es válido, procesa la petición

### Dependencias de autenticación

```python
from fastapi import Depends
from app.dependencies import get_current_user, get_admin_user

# Usuario autenticado (cualquier rol)
@router.get("/ruta")
async def mi_ruta(user: dict = Depends(get_current_user)):
    # user contiene: user_id, username, email, full_name, role
    pass

# Solo administradores
@router.post("/ruta-admin")
async def ruta_admin(user: dict = Depends(get_admin_user)):
    # Solo usuarios con role="admin"
    pass
```

## 📦 Modelo de Producto

```python
{
    "id": "uuid",
    "name": "Nombre del producto",
    "keywords": ["keyword1", "keyword2"],
    "stock": 100,
    "description": "Descripción (generada por IA si no se proporciona)",
    "category": "Categoría (generada por IA si no se proporciona)",
    "is_active": true,  # Controla visibilidad pública
    "created_at": "2025-11-14T12:00:00Z",
    "updated_at": "2025-11-14T12:00:00Z"
}
```

### Campo `is_active`

- `true`: Producto visible para el público
- `false`: Producto oculto (solo visible para admin)

**Casos de uso**:
- Productos descontinuados
- Productos agotados temporalmente
- Productos en borrador
- Productos de temporada fuera de temporada

## 🛠️ Ejemplos de Uso

### 1. Listar productos públicos (sin autenticación)

```bash
curl http://localhost:8000/products
```

### 2. Crear producto (requiere admin)

```bash
# Primero hacer login
TOKEN=$(curl -X POST http://localhost:8003/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ejemplo.com","password":"admin123"}' \
  | jq -r '.token.access_token')

# Crear producto
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Gaming",
    "keywords": ["laptop", "gaming", "nvidia"],
    "stock": 10,
    "is_active": true
  }'
```

### 3. Actualizar producto (requiere admin)

```bash
curl -X PUT http://localhost:8000/products/{product_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock": 15,
    "is_active": true
  }'
```

### 4. Desactivar producto (requiere admin)

```bash
curl -X PUT http://localhost:8000/products/{product_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### 5. Vender producto (requiere autenticación)

```bash
curl -X POST http://localhost:8000/products/{product_id}/sell \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Ver todos los productos como admin

```bash
curl http://localhost:8000/products/admin/all \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# Microservicios
IA_SERVICE_URL=http://microservicio-ia:8001
ALERTS_SERVICE_URL=http://microservicio-alertas:8002
AUTH_SERVICE_URL=http://microservicio-auth:8003

# Configuración
PORT=8000
LOW_STOCK_THRESHOLD=10
ALLOWED_ORIGINS=http://localhost:5173

# Claves de IA
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Timeouts
TIMEOUT_IA_SERVICE=35
ALERTS_WEBHOOK_TIMEOUT=10
```

## 🏗️ Estructura del Proyecto

```
app/
├── __init__.py
├── main.py                 # Aplicación FastAPI
├── config.py               # Configuración
├── database.py             # Conexión a BD
├── models.py               # Modelos SQLAlchemy
├── schemas.py              # Schemas Pydantic
├── dependencies.py         # Dependencias (auth, etc)
├── auth_client.py          # Cliente para microservicio auth
├── routes/
│   ├── __init__.py
│   ├── health.py          # Health checks
│   └── products.py        # Rutas de productos
├── services/
│   ├── __init__.py
│   └── product_service.py # Lógica de negocio
└── infraestructure/
    ├── __init__.py
    └── ia_client.py       # Cliente para microservicio IA
```

## 🚦 Flujo de Creación de Producto

1. Admin envía datos del producto
2. Si no hay descripción → genera con IA (keywords + nombre)
3. Si no hay categoría → genera con IA (nombre + descripción)
4. Guarda en base de datos
5. Retorna producto creado

## 🚦 Flujo de Venta de Producto

1. Usuario envía solicitud de venta
2. Verifica que el producto esté activo
3. Verifica que haya stock disponible
4. Reduce stock en 1
5. Guarda cambios
6. Si stock < threshold → envía alerta asíncrona
7. Retorna producto actualizado

## 📊 Integración con Microservicios

### Microservicio IA

- **Endpoint**: `/generate-description`, `/generate-category`
- **Uso**: Generación automática de contenido
- **Timeout**: 35 segundos

### Microservicio Alertas

- **Endpoint**: `/webhook/stock-alert`
- **Uso**: Notificaciones de stock bajo
- **Timeout**: 10 segundos
- **Asíncrono**: No bloquea la venta

### Microservicio Auth

- **Endpoint**: `/auth/verify`
- **Uso**: Validación de tokens JWT
- **Timeout**: 5 segundos

## 🧪 Testing

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
pytest

# Test manual con script
./test_auth.sh
```

## 📝 Notas de Desarrollo

### Productos Activos vs Inactivos

**Vista pública** (`GET /products`):
- Solo muestra productos con `is_active=True`
- Usuarios no autenticados pueden ver el catálogo

**Vista admin** (`GET /products/admin/all`):
- Muestra TODOS los productos (activos e inactivos)
- Requiere autenticación de administrador

### Permisos

- **Público**: Listar y ver productos activos
- **Usuario autenticado**: + Vender productos
- **Admin**: + Crear, editar, eliminar, ver inactivos

## 🐛 Troubleshooting

### Error 401 - No autorizado

- Verifica que el token JWT sea válido
- Asegúrate de incluir el header `Authorization: Bearer <token>`
- Verifica que el token no haya expirado

### Error 403 - Prohibido

- El usuario no tiene rol de administrador
- Verifica el rol en la base de datos: `SELECT role FROM users WHERE email='...'`
- Para cambiar a admin: `UPDATE users SET role='admin' WHERE email='...'`

### Producto no aparece en lista pública

- Verifica que `is_active=true`
- Consulta directa: `SELECT is_active FROM products WHERE id='...'`
- Para activar: `UPDATE products SET is_active=true WHERE id='...'`

## 📚 Documentación Adicional

- [Guía de Autenticación](AUTH_GUIDE.md)
- [OpenAPI/Swagger](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

## 🤝 Contribuir

1. Crear rama feature
2. Hacer cambios
3. Escribir tests
4. Crear pull request

## 📄 Licencia

MIT
