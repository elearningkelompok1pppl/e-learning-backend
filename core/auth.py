from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# =====================================================
# 🔐 ENV & CONFIG
# =====================================================
load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =====================================================
# 🔑 PASSWORD UTILS (SAFE VERSION)
# =====================================================
def _sanitize_password(password: str) -> bytes:
    """
    Pastikan password aman (encoded dan max 72 byte).
    """
    encoded = password.encode("utf-8", errors="ignore")
    if len(encoded) > 72:
        encoded = encoded[:72]
    return encoded


def hash_password(password: str) -> str:
    """
    Hash password secara aman (terhindar dari limit bcrypt 72 byte).
    """
    safe_pw = _sanitize_password(password)
    return pwd_context.hash(safe_pw.decode("utf-8", errors="ignore"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password dengan potongan byte aman.
    """
    safe_pw = _sanitize_password(plain_password)
    return pwd_context.verify(safe_pw.decode("utf-8", errors="ignore"), hashed_password)


# =====================================================
# 🧾 JWT UTILS
# =====================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Membuat JWT access token dengan payload data.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Verifikasi token JWT dan mengembalikan payload jika valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token telah kedaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract user info from JWT Access Token
    """
    payload = verify_access_token(token)

    if "sub" not in payload or "role" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung informasi user yang lengkap",
        )

    return {
        "sub": payload["sub"],  
        "role": payload["role"], 
    }