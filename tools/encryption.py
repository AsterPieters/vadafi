# encryption.py

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import argparse
import base64
import json
import os

def encrypt_secret(master_secret, plain_text_secret):
    """
    Encrypt a plain text secret using the master password.

    Args:
        master_secret (str): The master secret.
        plain_text_secret (str): The to be encrypted secret in plain text.
    
    Returns:
        secret_data (dict): A dictionary with the salt, iv and encrypted secret.
    """

    # Generate a random salt
    salt = os.urandom(16)

    # Key derivation function
    # This function will make it harder to bruteforce the master secret
    kdf = PBKDF2HMAC(

        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    # "Dirive" the key from the master secret
    encryption_key = kdf.derive(master_secret.encode())

    # Generate a random IV
    iv = os.urandom(12)
    
    # Encrypt the secret
    # The plain_text_secret should be encoded to be sure
    aesgcm = AESGCM(encryption_key)
    encrypted_secret = aesgcm.encrypt(iv, plain_text_secret.encode(), None)

    # Put all values in a dictionary
    # We encode the values for easier storage
    secret_data = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8'),
        "secret": base64.b64encode(encrypted_secret).decode('utf-8')
    }

    return json.dumps(secret_data)



def decrypt_secret(master_secret, secret_data):
    """
    Decrypt a secret using the master secret.

    Args:
        master_secret (str): The master secret.
        secret_data (dict): A dictionary with the salt, iv and encrypted secret.
    
    Returns:
        plain_text_secret (str): the plain_text_secret.
    """

    secret_data = json.loads(secret_data)

    # Grab the data out of the dictionary
    salt = base64.b64decode(secret_data['salt'])
    iv = base64.b64decode(secret_data['iv'])
    secret = base64.b64decode(secret_data['secret'])

    # Key derivation function 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
 
    # "Derive" the key from the master secret
    encryption_key = kdf.derive(master_secret.encode())
   
    # Decrypt the secret
    aesgcm = AESGCM(encryption_key)
    decrypted_secret = aesgcm.decrypt(iv, secret, None)
    plain_text_secret = decrypted_secret.decode()

    return plain_text_secret



def hash_secret(secret):
    """
    Hashes the secret.

    Args:
        secret (str): A secret.
    
    Returns:
        json_hashed_secret (JSON): A dictionary with the salt and hashed_secret.    
    """

    # Generate a random salt
    salt = os.urandom(16)

    # Key derivation function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    # Hash the secret
    secret_hash = kdf.derive(secret.encode())

    # Put the values in a dictionary
    hashed_data = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "secret_hash": base64.b64encode(secret_hash).decode('utf-8')
    }

    return json.dumps(hashed_data)



if __name__ == "__main__":
    
    # Initiate result
    result = None
    
    parser = argparse.ArgumentParser(description="Encrypt or decrypt secrets using a master secret.")
  
    # Subparser for action
    subparsers = parser.add_subparsers(dest="action", required=True, help="Specify action to perform.")

    # Subparser for encrypt
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a secret.")
    encrypt_parser.add_argument("master_secret", help="The password to use for encryption or decryption.")
    encrypt_parser.add_argument("plain_text_secret", help="The secret to be encrypted.")
    
    # Subparser for decrypt
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a secret.")
    decrypt_parser.add_argument("master_secret", help="The password to use for encryption or decryption.")
    decrypt_parser.add_argument("secret_data", help="Dictionary with salt, iv and password.")
    
    # Now parse all arguments
    args = parser.parse_args()

    # Encrypt the secret
    if args.action == "encrypt":
        result = encrypt_secret(args.master_secret, args.plain_text_secret)
        
    # Decrypt the secret
    elif args.action == "decrypt":
        result = decrypt_secret(args.master_secret, args.secret_data)

    # Print the final result
    print(result)
