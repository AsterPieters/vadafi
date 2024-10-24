# Vadafi.py

import argparse

from modules.tools.encryption import encrypt_secret, decrypt_secret
from modules.secrets import add_secret
from modules.secrets import list_secrets
from modules.users import create_user

# Initiate result
result = None

# Parser
parser = argparse.ArgumentParser(description="Manage vadafi recources.")

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

# Subparser for create_user
create_user_parser = subparsers.add_parser("create_user", help="Create a user.")
create_user_parser.add_argument("username", help="The username to manage.")
create_user_parser.add_argument("master_secret", help="The master secret of the user.")

# Subparser for add_secret
add_secret_parser = subparsers.add_parser("add_secret", help="Add a secret.")
add_secret_parser.add_argument("username", help="The user's username.")
add_secret_parser.add_argument("master_secret", help="The user's master secret.")
add_secret_parser.add_argument("secret_name", help="The secret's name.")
add_secret_parser.add_argument("plain_text_secret", help="The secret in plain text.")

# Subparser for list_secrets
list_secrets_parser = subparsers.add_parser("list_secrets", help="List all secrets of a user.")
list_secrets_parser.add_argument("username", help="The user's username.")
list_secrets_parser.add_argument("master_secret", help="The user's master secret.")

# Now parse all arguments
args = parser.parse_args()

# Encrypt the secret
if args.action == "encrypt":
    result = encrypt_secret(args.master_secret, args.plain_text_secret)
    
# Decrypt the secret
elif args.action == "decrypt":
    result = decrypt_secret(args.master_secret, args.secret_data)

# Encrypt the secret
if args.action == "create_user":
    result = create_user(args.username, args.master_secret)

# Add a secret
if args.action == "add_secret":
    result = add_secret(args.username, args.master_secret, args.secret_name, args.plain_text_secret)

# Lists all secrets for a user
if args.action == "list_secrets":
    result = list_secrets(args.username, args.master_secret)

# Print the final result
if result:
    print(result)

