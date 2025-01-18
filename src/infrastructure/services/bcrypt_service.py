from typing import cast

from passlib.context import CryptContext

from src.configs.logger import log

# Create a password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return cast(str, pwd_context.hash(password))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        log.info(f"Plain password: {plain_password}")
        log.info(f"Hashed password: {hashed_password}")
        return cast(bool, pwd_context.verify(plain_password, hashed_password))
