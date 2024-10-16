# users.py

import re
import base64
import json
import argparse

from tools.encryption import hash_password

def check_username_validity(username):
    return re.match("^[a-zA-Z0-9_]{1,30}$", username) is not None

def create_user(user_name, master_secret):
    """
    Creates a user, hashed the password, and stores the information in the database.

    Args:
        user_name (str): A unique username.
        master_secret (str): The users master_secret.
    
    Returns:
        bool: True if created succesfully.

    Raises:
        Exception: If creation was unsuccesful.
    """

    if check_username_validity(user_name):
        print("test")
    else:
        raise ValueError ("Invalid username")


    # Hash the password and load json
    json_hashed_password = hash_password(master_secret)
    hashed_password = json.loads(json_hashed_password)

    # Decode the values
    salt = base64.b64decode(hashed_password["salt"]).decode('utf-8')
    password_hash = base64.b64decode(hashed_password["password_hash"]).decode('utf-8')

    return salt, password_hash



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Manage users.")
    parser.add_argument("action", choices=["create", "remove"], help="Specify whether to create or remove a user.")
    parser.add_argument("user_name", help="The username to manage.")
    
    parser.add_argument("master_secret", help="The master secret of the user.")
    
    args = parser.parse_args()

    # Encrypt the secret
    if args.action == "create":
        result = create_user(args.user_name, args.master_secret)
        
    # Print the final result
    print(result)
