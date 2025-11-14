# Autenticación en el Backend Principal

Este documento explica cómo usar el sistema de autenticación integrado con el microservicio de auth.

## 🔐 Visión General

El backend principal se comunica con el microservicio de autenticación para validar tokens JWT. Esto permite proteger rutas específicas mientras se mantienen otras rutas públicas.

## 🎯 Dependencias Disponibles

### 1. `get_current_user` - Usuario autenticado

Valida que el usuario esté autenticado (cualquier rol).

```python
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/mi-perfil")
async def get_profile(user: dict = Depends(get_current_user)):
    # user contiene: {"user_id": "...", "username": "...", "email": "...", "full_name": "...", "role": "..."}
    return {"message": f"Hola {user['full_name']}"}
```

### 2. `get_admin_user` - Solo administradores

Valida que el usuario esté autenticado **Y** tenga rol de administrador.

```python
from fastapi import APIRouter, Depends
from ..dependencies import get_admin_user

router = APIRouter()

@router.delete("/productos/{product_id}")
async def delete_product(
    product_id: str,
    user: dict = Depends(get_admin_user)
):
    # Solo usuarios con role="admin" pueden acceder aquí
    return {"message": "Producto eliminado"}
```

### 3. Sin dependencia - Rutas públicas

Simplemente no incluyas ninguna dependencia de autenticación.

```python
@router.get("/productos")
async def list_products():
    # Endpoint público - cualquiera puede acceder
    return {"products": [...]}
```

## 📋 Ejemplos de Uso

### Ejemplo 1: Catálogo público con gestión protegida

```python
from typing import List
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user, get_admin_user
from ..schemas import Product

router = APIRouter(prefix="/products")

# ✅ PÚBLICO - Sin autenticación
@router.get("", response_model=List[Product])
async def list_products():
    return get_all_products()

# 🔒 AUTENTICADO - Cualquier usuario
@router.post("/{id}/comprar")
async def buy_product(id: str, user: dict = Depends(get_current_user)):
    return process_purchase(id, user["user_id"])

# 🔐 ADMIN - Solo administradores
@router.post("", response_model=Product)
async def create_product(product: Product, user: dict = Depends(get_admin_user)):
    return create_new_product(product)

@router.delete("/{id}")
async def delete_product(id: str, user: dict = Depends(get_admin_user)):
    return remove_product(id)
```

### Ejemplo 2: Rutas de usuario

```python
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/users")

@router.get("/me")
async def get_my_profile(user: dict = Depends(get_current_user)):
    return {
        "id": user["user_id"],
        "email": user["email"],
        "name": user["full_name"],
        "role": user["role"]
    }

@router.put("/me/password")
async def change_password(
    new_password: str,
    user: dict = Depends(get_current_user)
):
    update_user_password(user["user_id"], new_password)
    return {"message": "Contraseña actualizada"}
```

## 🔄 Flujo de Autenticación

1. **Cliente** hace login en `/auth/login` (microservicio-auth)
2. **Microservicio Auth** retorna un token JWT
3. **Cliente** incluye el token en las peticiones: `Authorization: Bearer <token>`
4. **Backend Principal** valida el token con el microservicio-auth
5. Si es válido, la petición continúa con los datos del usuario

## 🛠️ Configuración

### Variables de Entorno

```bash
# En docker-compose.yml o .env del backend-principal
AUTH_SERVICE_URL=http://microservicio-auth:8001
```

### Estructura del Token

El token JWT contiene:
```json
{
  "sub": "user_id",
  "exp": 1234567890
}
```

### Respuesta de Verificación

Cuando se valida un token, se retorna:
```json
{
  "user_id": "123",
  "username": "usuario@ejemplo.com",
  "email": "usuario@ejemplo.com",
  "full_name": "Juan Pérez",
  "role": "admin"
}
```

## 🧪 Testing

### Con cURL

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ejemplo.com","password":"admin123"}' \
  | jq -r '.token.access_token')

# 2. Usar el token en ruta protegida
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Producto","price":100,"stock":50}'
```

### Con HTTPie

```bash
# 1. Login
http POST :8001/auth/login email=admin@ejemplo.com password=admin123

# 2. Guardar token
TOKEN="tu_token_aqui"

# 3. Usar token
http POST :8000/products Authorization:"Bearer $TOKEN" name="Producto" price:=100 stock:=50
```

## 🚨 Manejo de Errores

### 401 Unauthorized
- Token no proporcionado
- Token inválido o expirado
- Token mal formateado

```json
{
  "detail": "Token inválido o expirado"
}
```

### 403 Forbidden
- Usuario autenticado pero sin permisos suficientes
- Intentó acceder a ruta de admin sin ser admin

```json
{
  "detail": "Se requieren permisos de administrador"
}
```

## 💡 Buenas Prácticas

1. **Rutas públicas por defecto**: Solo protege lo que necesitas
2. **Usa `get_current_user`** para operaciones de usuario normal
3. **Usa `get_admin_user`** solo para operaciones administrativas críticas
4. **Loguea acciones importantes**: Incluye el username en los logs
5. **Maneja errores de auth gracefully**: Retorna mensajes claros

## 🔧 Troubleshooting

### El token no se valida

- Verifica que `AUTH_SERVICE_URL` apunte correctamente al microservicio
- Asegúrate de que ambos servicios usen la misma `JWT_SECRET_KEY`
- Revisa los logs del microservicio-auth

### Timeout al validar token

- El microservicio de auth no está respondiendo
- Aumenta el timeout en `auth_client.py` si es necesario

### Usuario no puede acceder a ruta

- Verifica que el token no haya expirado
- Confirma que el usuario tenga el rol correcto (para rutas admin)
