"""
This file contains cryptographic utilities for the secure messaging system.
In a real application, you would use proper cryptographic libraries.
This is a simplified implementation for demonstration purposes.
"""

import os
import hashlib
import hmac as hmac_lib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def generate_key():
    """Generate a random AES key"""
    return os.urandom(32)  # 256-bit key

def derive_key(password, salt=None):
    """Derive a key from a password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    
    # Use PBKDF2 to derive a key from the password
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    
    return key, salt

def encrypt_aes(plaintext, key, mode='CBC', iv=None):
    """
    Encrypt data using AES
    
    Args:
        plaintext (str): The text to encrypt
        key (bytes): The encryption key
        mode (str): The encryption mode (ECB, CBC, CFB, OFB, CTR)
        iv (bytes, optional): Initialization vector for modes that require it
    
    Returns:
        tuple: (ciphertext, iv)
    """
    plaintext_bytes = plaintext.encode('utf-8')
    
    # Add padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()
    
    # Select the appropriate mode
    if mode == 'ECB':
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        iv = None
    elif mode == 'CBC':
        if iv is None:
            iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    elif mode == 'CFB':
        if iv is None:
            iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    elif mode == 'OFB':
        if iv is None:
            iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend())
    elif mode == 'CTR':
        if iv is None:
            iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    
    # Encrypt the data
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return ciphertext, iv

def decrypt_aes(ciphertext, key, mode='CBC', iv=None):
    """
    Decrypt data using AES
    
    Args:
        ciphertext (bytes): The encrypted data
        key (bytes): The decryption key
        mode (str): The encryption mode (ECB, CBC, CFB, OFB, CTR)
        iv (bytes, optional): Initialization vector used for encryption
    
    Returns:
        str: The decrypted text
    """
    # Select the appropriate mode
    if mode == 'ECB':
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    elif mode == 'CBC':
        if iv is None:
            raise ValueError("IV is required for CBC mode")
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    elif mode == 'CFB':
        if iv is None:
            raise ValueError("IV is required for CFB mode")
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    elif mode == 'OFB':
        if iv is None:
            raise ValueError("IV is required for OFB mode")
        cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend())
    elif mode == 'CTR':
        if iv is None:
            raise ValueError("IV is required for CTR mode")
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    
    # Decrypt the data
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext_bytes.decode('utf-8')

def create_hmac(message, key):
    """Create an HMAC for message authentication"""
    h = hmac_lib.new(key, message, hashlib.sha256)
    return h.hexdigest()

def verify_hmac(message, key, hmac_value):
    """Verify an HMAC for message authentication"""
    h = hmac_lib.new(key, message, hashlib.sha256)
    calculated_hmac = h.hexdigest()
    return hmac_lib.compare_digest(calculated_hmac, hmac_value)

