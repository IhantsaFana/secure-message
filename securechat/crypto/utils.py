import os
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_message(key: bytes, plaintext: str):
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # HMAC
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(ciphertext)
    tag = h.finalize()

    return b64encode(ciphertext).decode(), b64encode(iv).decode(), b64encode(tag).decode()

def decrypt_message(key: bytes, ciphertext_b64: str, iv_b64: str):
    ciphertext = b64decode(ciphertext_b64)
    iv = b64decode(iv_b64)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    return plaintext.decode()
