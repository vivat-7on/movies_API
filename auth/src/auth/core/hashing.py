import hashlib

from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.verify(password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
