"""Cliente HTTP para comunicarse con el microservicio de autenticación."""
import httpx
from .config import AUTH_SERVICE_URL, logger


async def verify_token(token: str) -> dict | None:
    """
    Verifica un token JWT con el microservicio de autenticación.
    
    Args:
        token: El token JWT a verificar
        
    Returns:
        dict con los datos del usuario si el token es válido, None si no lo es
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(
                    "token_verified",
                    username=data.get("username"),
                    role=data.get("role")
                )
                return data
            else:
                logger.warning(
                    "token_verification_failed",
                    status_code=response.status_code
                )
                return None
                
    except httpx.TimeoutException:
        logger.error("auth_service_timeout", url=AUTH_SERVICE_URL)
        return None
    except Exception as e:
        logger.error("auth_service_error", error=str(e))
        return None
