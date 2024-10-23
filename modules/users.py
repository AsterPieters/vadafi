# users.py

import re
import psycopg2
from psycopg2.errors import QueryCanceled
from flask import jsonify

from .tools.encryption import hash_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger
from .tools.authentication import get_admin_dbconfig

logger = vadafi_logger()

def check_username_validity(username):
    return re.match("^[a-zA-Z0-9_]{1,30}$", username) is not None



def check_username_availability(username):
    """
    Check if username is available in the vadafi_users table.
    """
    try:
        # Get the dbconfig
        dbconfig = get_admin_dbconfig()

        # Create the query
        query = """
        SELECT COUNT(*) FROM vadafi_users WHERE username = %s
        """
        result = execute_query(
            query,
            params=(username,),
            return_data=True,
            dbconfig=dbconfig
            )
        if result[0][0] == 0:
            return True
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error occured while checking username availability.")
        return False



def get_user_id(username):
    """
    Get the unique identifier of a user.
    """

    # Get the dbconfig
    dbconfig = get_admin_dbconfig()    

    # Create the query
    query="""
    SELECT user_id FROM vadafi_users WHERE username = %s
    """

    # Get the user_id
    result = execute_query(
       query,
       params=(username, ),
       return_data=True,
       dbconfig=dbconfig
        )
    if result:
        return result[0][0]
    else:
        return None



def create_user(data):
    """
    Creates a user, hashes the secret, and stores the information in the database.

    Args:
        data (dict): A dictionary with the user and password.
    
    Returns:
        bool: True if created succesfully.
    """

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data:
        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username and password are required."
        }), 400

    # Get data from dict
    username = data['username']
    master_secret = data['password']

    # Check if username is valid
    if check_username_validity(username):
        pass
    else:
        # Return username not valid
        return jsonify({
            "error": "Username not valid",
            "message": "Sorry, this username is not valid."
        }), 200

    # Check if username is available
    if check_username_availability(username):
        pass
    else:
        # Return username not available
        return jsonify({
            "error": "Username unavailable",
            "message": "Sorry, this username is not available."
        }), 200

    try:
        # Get the dbconfig for the vadafi database
        vadafi_dbconfig = get_admin_dbconfig()

        # Hash the master secret
        hashed_data = hash_secret(master_secret)

        # Add user to vadafi_users
        query="""
        INSERT INTO vadafi_users (username, master_secret_hash, salt)
        VALUES (%s, %s, %s)
        """
        execute_query(
            query,
            params=(username, hashed_data["secret_hash"], hashed_data["salt"]),
            dbconfig=vadafi_dbconfig
            )
        logger.info(f"Created user {username} in vadafi_users table.")
    
        # Name database & database_user based on user's unique identifier
        user_id = get_user_id(username) 
        db_name = f"db_{user_id}"
        db_user_name = f"user_{user_id}"

        # Get the dbconfig for the user database
        # This will also be as the admin
        user_dbconfig = get_admin_dbconfig(db_name)
        
        # Create database
        execute_query(
            f"CREATE DATABASE {db_name}",
            autocommit=True,
            dbconfig=vadafi_dbconfig
            )
        logger.info(f"Created {db_name}.")

        # Create database user
        execute_query(
            f"CREATE USER {db_user_name} WITH PASSWORD %s",
            params=(master_secret,),
            dbconfig=vadafi_dbconfig
            )
        logger.info(f"Created {db_user_name}.")

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
        execute_query(
                query, 
                dbconfig=user_dbconfig
                )
        logger.info(f"Created table 'secrets' on {db_name}.")

        # Configure the user's privileges
        execute_query(f"ALTER DATABASE {db_name} OWNER TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"ALTER SCHEMA public OWNER TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"GRANT USAGE, CREATE ON SCHEMA public TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"ALTER TABLE public.secrets OWNER TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user_name};", dbconfig=user_dbconfig)
        execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {db_user_name};", dbconfig=user_dbconfig)
        logger.info(f"Configured privileges for {db_user_name} in database {db_name}.")

        # Log the success
        logger.info(f"Succesfully created user {username}!")

        return jsonify({
            "message": "User created succesfully."
        }), 200

    except Exception as e:
        logger.error(f"Error occured while trying to create user {username} in vadafi database {e}")
        
        # Return error
        return jsonify({
            "error": "Error occured creating user",
            "message": "Sorry, we could not create your user at this moment."
        }), 400
