import hashlib


def verify_token(stored_hashed_token: str, provided_token: str):
    provided_hashed_token = hashlib.sha256(provided_token.encode()).hexdigest()
    return stored_hashed_token == provided_hashed_token
