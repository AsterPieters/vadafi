# users.py

import re
import base64
import json
import argparse
import psycopg2

from tools.encryption import hash_secret
from tools.execute_query import execute_query

from tools.logger import vadafi_logger

logger = vadafi_logger()

def check_username_validity(username):
    return re.match("^[a-zA-Z0-9_]{1,30}$", username) is not None

def create_user(username, master_secret):
    """
    Creates a user, hashes the secret, and stores the information in the database.

    Args:
        username (str): A unique username.
        master_secret (str): The users master_secret.
    
    Returns:
        bool: True if created succesfully.

    Raises:
        Exception: If creation was unsuccesful.
    """

    # Check if username is valid
    if check_username_validity(username):
        pass
    else:
        raise ValueError ("Invalid username")
    
    # Create user row in vadafi-users
    try:
        # Hash the master secret
        hashed_data = json.loads(hash_secret(master_secret))

        # Create the query
        query = """
        INSERT INTO vadafi_users (username, master_secret_hash, salt)
        VALUES (%s, %s, %s)
        """

        # Set the params
        params = (username, hashed_data["secret_hash"], hashed_data["salt"])

        # Create user in vadafi's database
        execute_query(query, False, params)

        # Create the user's database
        execute_query(f"CREATE DATABASE {username}", autocommit=True)
        logger.info(f"Created database {username}.")

        # Create user in postgres
        execute_query(f"CREATE USER {username} WITH PASSWORD '{master_secret}';")
        logger.info(f"Created user {username}.")

        # Grant privileges to user for user's database
        execute_query(f"GRANT ALL PRIVILEGES ON DATABASE {username} TO {username};")
        logger.info(f"Granted privileges on database {username} to {username}.")

    except psycopg2.errors.UniqueViolation:
        logger.error(f"Username {username} is already taken.")

    except Exception as e:
        logger.error(f"Error occured while trying to create user: {e}")




if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Manage users.")
    parser.add_argument("action", choices=["create", "remove"], help="Specify whether to create or remove a user.")
    parser.add_argument("username", help="The username to manage.")
    
    parser.add_argument("master_secret", help="The master secret of the user.")
    
    args = parser.parse_args()

    # Encrypt the secret
    if args.action == "create":
        result = create_user(args.username, args.master_secret)
