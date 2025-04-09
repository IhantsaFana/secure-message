from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
import os

# Génération de la paire RSA
def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Sérialisation
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # chiffré plus tard
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

# Chiffrer la clé privée avec le mot de passe de l’utilisateur
def encrypt_private_key(private_key_bytes, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=390000, backend=default_backend()
    )
    key = kdf.derive(password.encode())

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    from cryptography.hazmat.primitives import padding
    padder = padding.PKCS7(128).padder()
    padded = padder.update(private_key_bytes) + padder.finalize()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    return b64encode(salt + iv + encrypted).decode()

def decrypt_private_key(encrypted_data_b64, password):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding

    encrypted_data = b64decode(encrypted_data_b64)
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_key = encrypted_data[32:]

    # Dérive la même clé AES à partir du mot de passe
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=390000, backend=default_backend()
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_key) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    private_key = unpadder.update(decrypted_padded) + unpadder.finalize()
    return private_key  # bytes


# Déchiffrement de la clé AES avec la clé privée RSA
def decrypt_aes_key(encrypted_aes_key_b64, private_key_pem):
    from cryptography.hazmat.primitives import serialization

    # Charger la clé privée à partir de la clé PEM
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,  # On suppose que la clé est déjà déchiffrée
        backend=default_backend()
    )

    encrypted_aes_key = b64decode(encrypted_aes_key_b64)

    # Déchiffrement de la clé AES avec la clé privée RSA
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_key
