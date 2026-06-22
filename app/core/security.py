import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash bcrypt.
    Valida el formato del hash antes de procesarlo.
    """
    try:
        # Validar que el hash tenga formato bcrypt válido
        if not hashed_password or len(hashed_password) < 50:
            print(f"[ERROR] Hash inválido - longitud: {len(hashed_password)}")
            return False

        # Validar que comience con prefijo bcrypt válido
        if not hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            print(f"[ERROR] Hash no es bcrypt válido: {hashed_password[:20]}")
            return False

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    except (ValueError, TypeError) as e:
        print(f"[ERROR] Error verificando contraseña: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Genera un hash bcrypt seguro para una contraseña.
    """
    salt = bcrypt.gensalt(rounds=12)  # 12 rondas es estándar
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt,
    ).decode("utf-8")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}")
