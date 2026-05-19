"""Service for encrypting/decrypting integration tokens with key version metadata."""

import base64
import hashlib
import os
from typing import Optional, Tuple

from cryptography.fernet import Fernet, InvalidToken
from loguru import logger


class TokenCryptoService:
    """Token encryption/decryption service with key version support."""

    ENV_KEY = "ALWRITY_TOKEN_ENCRYPTION_KEY"
    ENV_KEY_VERSION = "ALWRITY_TOKEN_KEY_VERSION"

    def __init__(self):
        raw_key = os.getenv(self.ENV_KEY, "")
        if raw_key:
            self._fernet_key = self._normalize_key(raw_key)
        else:
            self._fernet_key = self._derive_dev_key()
        self._fernet = Fernet(self._fernet_key)
        self._key_version = os.getenv(self.ENV_KEY_VERSION, "v1")
        self._key_reference = self._fingerprint(self._fernet_key)

    @property
    def key_version(self) -> str:
        return self._key_version

    @property
    def key_reference(self) -> str:
        return self._key_reference

    def encrypt_token(self, token: Optional[str]) -> Optional[str]:
        if token is None:
            return None
        return self._fernet.encrypt(token.encode("utf-8")).decode("utf-8")

    def decrypt_token(self, encrypted_token: Optional[str]) -> Optional[str]:
        if encrypted_token is None:
            return None
        try:
            return self._fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            logger.error("Token decryption failed due to invalid token/key")
            raise

    def encrypt_pair(self, access_token: str, refresh_token: Optional[str]) -> Tuple[str, Optional[str]]:
        return self.encrypt_token(access_token), self.encrypt_token(refresh_token)

    @staticmethod
    def _normalize_key(raw_key: str) -> bytes:
        raw_key = raw_key.strip()
        if len(raw_key) == 44 and raw_key.endswith("="):
            return raw_key.encode("utf-8")
        digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def _derive_dev_key() -> bytes:
        seed = "alwrity-local-token-key"
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def _fingerprint(key: bytes) -> str:
        return hashlib.sha256(key).hexdigest()[:16]
