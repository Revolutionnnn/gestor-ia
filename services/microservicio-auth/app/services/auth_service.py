from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import PASSWORD_MIN_LENGTH, logger
from ..security import create_access_token, hash_password, verify_password


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(
    db: Session,
    payload: schemas.UserCreate,
) -> schemas.AuthResponse:
    email = _normalize_email(payload.email)
    if len(payload.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "La contraseña debe tener al menos "
                f"{PASSWORD_MIN_LENGTH} caracteres"
            ),
        )

    user = models.User(
        email=email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        logger.info("register_conflict", email=email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    token, expires_in = create_access_token(subject=str(user.id))
    return schemas.AuthResponse(
        user=schemas.UserRead.model_validate(user),
        token=schemas.Token(access_token=token, expires_in=expires_in),
    )


def login_user(
    db: Session,
    payload: schemas.UserLogin,
) -> schemas.AuthResponse:
    email = _normalize_email(payload.email)
    user = (
        db.query(models.User)
        .filter(models.User.email == email)
        .one_or_none()
    )

    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning("login_failed", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token, expires_in = create_access_token(subject=str(user.id))
    return schemas.AuthResponse(
        user=schemas.UserRead.model_validate(user),
        token=schemas.Token(access_token=token, expires_in=expires_in),
    )
