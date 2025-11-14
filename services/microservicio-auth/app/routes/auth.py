from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registra un usuario y retorna sus credenciales JWT."""
    return auth_service.register_user(db, payload)


@router.post(
    "/login",
    response_model=schemas.AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuario",
)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """Valida credenciales y emite un token JWT de acceso corto."""
    return auth_service.login_user(db, payload)


@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verificar token JWT",
)
def verify_token(token: str = Depends(auth_service.get_current_user_from_token)):
    """
    Verifica la validez de un token JWT y retorna los datos del usuario.
    
    Este endpoint es usado por otros microservicios para validar tokens.
    """
    return token
