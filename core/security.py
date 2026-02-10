import secrets
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.hazmat.primitives import hashes

class SecurityManager:
    def __init__(self):
        pass

    @staticmethod
    def hash_key(key: bytes) -> bytes:
        """
        Hashes the derived key to create a verifier for the DB.
        This allows checking if the password is correct without storing the key.
        """
        digest = hashes.Hash(hashes.SHA256())
        digest.update(key)
        return digest.finalize()

    @staticmethod
    def generate_salt(length=16) -> bytes:
        """Generates a random salt."""
        return secrets.token_bytes(length)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derives a key from the password using Argon2id via argon2-cffi.
        """
        return hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=2,
            memory_cost=64 * 1024,  # 64 MB
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )

    @staticmethod
    def encrypt(data: str, key: bytes) -> tuple[bytes, bytes]:
        """
        Encrypts data using AES-GCM.
        Returns (nonce, ciphertext).
        """
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        return nonce, ciphertext

    @staticmethod
    def decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> str:
        """
        Decrypts data using AES-GCM.
        """
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
