import asyncio
import hashlib

from passlib.hash import bcrypt


async def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return await asyncio.to_thread(bcrypt.hash, password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return asyncio.to_thread(bcrypt.verify, password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
