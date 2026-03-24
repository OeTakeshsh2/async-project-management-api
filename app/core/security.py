from passlib.context import CryptContext
from app.core.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_user_token(email: str) -> str:
    access_token = create_access_token(
        data={"sub": email}
    )
    return access_token
