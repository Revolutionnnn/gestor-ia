from typing import Optional

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from .auth_client import verify_token
from .database import get_db
from .models import Product


def get_product_or_404(
    product_id: str,
    db: Session = Depends(get_db),
) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


async def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependencia de FastAPI para verificar autenticación en rutas protegidas.
    
    Uso:
        @router.post("/ruta-protegida")
        async def mi_ruta(user: dict = Depends(get_current_user)):
            # user contendrá: {"username": "...", "role": "...",
            # "user_id": "..."}
            pass
    
    Args:
        authorization: Header "Authorization" con formato "Bearer <token>"
        
    Returns:
        dict con los datos del usuario autenticado
        
    Raises:
        HTTPException 401 si no hay token o el token es inválido
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer el token del header "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema de autenticación inválido")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar el token con el microservicio de auth
    user_data = await verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependencia de FastAPI que requiere que el usuario sea administrador.
    
    Uso:
        @router.delete("/productos/{id}")
        async def eliminar_producto(user: dict = Depends(get_admin_user)):
            # Solo usuarios con role="admin" pueden acceder aquí
            pass
    
    Args:
        current_user: Usuario autenticado (inyectado automáticamente)
        
    Returns:
        dict con los datos del usuario administrador
        
    Raises:
        HTTPException 403 si el usuario no es administrador
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    
    return current_user


async def get_optional_user(
    authorization: str = Header(None),
) -> Optional[dict]:
    """Devuelve al usuario autenticado si se envía token o None en otro caso.

    Permite exponer rutas públicas con capacidades adicionales cuando el
    usuario se autentica voluntariamente.
    """
    if not authorization:
        return None

    try:
        # type: ignore[arg-type] se usa porque forzamos la firma manualmente
        return await get_current_user(authorization)
    except HTTPException:
        # En caso de token inválido, consideramos la petición como anónima
        return None
