import hashlib
import secrets


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def generate_enrollment_token() -> str:
    return secrets.token_urlsafe(32)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

def hash_enrollment_token(token: str) -> str:
    return hash_secret(token)