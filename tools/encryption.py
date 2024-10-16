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
    """ Encrypt secrets using the master secret and return them in a json string """
    
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
    aesgcm = AESGCM(encryption_key)
    encrypted_secret = aesgcm.encrypt(iv, plain_text_secret.encode(), None)

    # Put all values in a dictionary
    # We decode the values in order to properly store them
    secret_data = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8'),
        "secret": base64.b64encode(encrypted_secret).decode('utf-8')
    }

    # Convert to JSON
    json_secret_data = json.dumps(secret_data)
    
    return json_secret_data



def decrypt_secret(master_secret, secret_data):
    """ Decrypt secrets using the master secret """

    # Load the JSON string
    decoded_secret_data = json.loads(secret_data)

    # Grab the data out of the dictionary
    salt = base64.b64decode(decoded_secret_data["salt"])
    iv = base64.b64decode(decoded_secret_data['iv'])
    secret = base64.b64decode(decoded_secret_data['secret'])

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



def hash_password(password):
    """
    Hashes the password.

    Args:
        password (str): A password.
    
    Returns:
        json_hashed_password (JSON): A dictionary with the salt and hashed_password.    
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

    # Hash the password
    password_hash = kdf.derive(password.encode())

    # Put the values in a dictionary
    hashed_password = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "password_hash": base64.b64encode(password_hash).decode('utf-8')
    }

    # Convert to json
    json_hashed_password = json.dumps(hashed_password)

    return json_hashed_password



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Encrypt or decrypt secrets using a master secret.")
    parser.add_argument("action", choices=["encrypt", "decrypt"], help="Specify whether to encrypt or decrypt the secret.")
    parser.add_argument("master_secret", help="The password to use for encryption or decryption.")
    
    parser.add_argument("plain_text_secret", help="The secret to be encrypted")
    parser.add_argument("secret_data", help="The secret to be decrypted", nargs='?', default=None)
    
    args = parser.parse_args()

    # Encrypt the secret
    if args.action == "encrypt":
        result = encrypt_secret(args.master_secret, args.plain_text_secret)
        
    # Decrypt the secret
    elif args.action == "decrypt":
        result = decrypt_secret(args.master_secret, args.secret_data)

    # Print the final result
    print(result)
