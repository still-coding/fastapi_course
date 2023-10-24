from passlib.context import CryptContext

password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_ctx.hash(password)


def verify_password(plain_pasword: str, hashed_password: str) -> bool:
    return password_ctx.verify(plain_pasword, hashed_password)
