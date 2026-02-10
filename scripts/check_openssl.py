from cryptography.hazmat.backends import default_backend
try:
    print(f"OpenSSL Version: {default_backend().openssl_version_text()}")
except Exception as e:
    print(f"Error getting OpenSSL version: {e}")

try:
    from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    print("Argon2id imported successfully.")
except ImportError:
    print("Argon2id import failed.")
