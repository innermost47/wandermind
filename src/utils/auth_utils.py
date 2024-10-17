import secrets


class AuthUtils:
    def generate_api_key(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)
