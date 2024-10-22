# users.py

import re
import os
import json
import argparse
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

from tools.encryption import hash_secret
from tools.execute_query import execute_query, execute_query

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

    # Create the vadafi admin credentials dict for query's on the user's database
    env_path = Path('.env')
    load_dotenv(env_path)
    credentials = {
    'dbname': username,
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
        }

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

        # Add user to vadafi_users
        execute_query(query, False, params)

        # Create database
        execute_query(f"CREATE DATABASE {username}", autocommit=True)
        logger.info(f"Created database: {username}.")

        # Create user
        execute_query(f"CREATE USER {username} WITH PASSWORD '{master_secret}';")
        logger.info(f"Created user: {username}.")

        # Create secret table
        query = """
        CREATE TABLE secrets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            secret TEXT NOT NULL,
            salt VARCHAR(255) NOT NULL,
            iv VARCHAR(255) NOT NULL
        );
        """
        execute_query(query, credentials=credentials)
        logger.info(f"Created table 'secrets' on database {username}.")

        # Configure the user's privileges
        execute_query(f"ALTER DATABASE {username} OWNER TO {username};", credentials=credentials)
        execute_query(f"ALTER SCHEMA public OWNER TO {username};", credentials=credentials)
        execute_query(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {username};", credentials=credentials)
        execute_query(f"GRANT USAGE, CREATE ON SCHEMA public TO {username};", credentials=credentials)
        execute_query(f"ALTER TABLE public.secrets OWNER TO {username};", credentials=credentials)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username};", credentials=credentials)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username};", credentials=credentials)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {username};", credentials=credentials)
        logger.info(f"Configured privileges for {username} in database {username}.")

        # Log the success
        logger.info(f"Succesfully created user: {username}!")

    except psycopg2.errors.UniqueViolation:
        logger.error(f"Username {username} is already taken.")

    except Exception as e:
        logger.error(f"Error occured while trying to create user: {username} in vadafi database: {e}")


