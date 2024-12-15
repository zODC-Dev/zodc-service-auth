from typing import cast

from passlib.context import CryptContext

# Create a password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password."""
    return cast(str, pwd_context.hash(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))
