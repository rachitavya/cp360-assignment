import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.conf import settings
import os

# 32 bytes key for AES-256
AES_SECRET_KEY = getattr(settings, 'AES_SECRET_KEY', b'supersecretkeymustbe32byteslong!!')
AES_BLOCK_SIZE = 128  # bits


def pad(data):
    padder = padding.PKCS7(AES_BLOCK_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data

def unpad(padded_data):
    unpadder = padding.PKCS7(AES_BLOCK_SIZE).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

def encrypt_data(data):
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    elif isinstance(data, str):
        data = data.encode()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(AES_SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = pad(data)
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode()

def decrypt_data(token):
    raw = base64.b64decode(token)
    iv = raw[:16]
    ct = raw[16:]
    cipher = Cipher(algorithms.AES(AES_SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    data = unpad(padded_data)
    try:
        return json.loads(data)
    except Exception:
        return data.decode() 