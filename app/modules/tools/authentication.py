# authentication.py

import base64

from flask import jsonify

from .execute_query import get_admin_dbconfig
from .execute_query import execute_query
from .encryption import hash_secret
from .logger import vadafi_logger

logger = vadafi_logger()

def user_exists(username):
    """
    Check if the user exits by querying the vadafi_users table
    """
    # Get the dbconfig
    dbconfig = get_admin_dbconfig()

    try:
        # Check if username exists
        result = execute_query(
                "SELECT 1 FROM vadafi_users WHERE username = %s", 
                params=(username,),
                return_data=True,
                dbconfig=dbconfig
            )
        
        if result:
            logger.info(f"User {username} exists.")
            return True
        else:
            logger.error(f"User {username} not found.")
            return False

    except Exception as e:
        logger.error(f"Error occured checking user: {username}'s existence. {e}")
        return False



def check_password(password, username):
    """
    Hash password and match it with the one in the database
    """

    # Get the dbconfig
    dbconfig = get_admin_dbconfig()

    try:
        # Get the salt and iv of the user
        result = execute_query(
            "SELECT salt, master_secret_hash FROM vadafi_users WHERE username = %s",
            params=(username,),
            return_data=True,
            dbconfig=dbconfig
            )
        
        # Get the data
        # Decode the salt and turn it into bytes
        salt = base64.b64decode(result[0][0].encode('utf-8'))
        master_secret_hash = result[0][1]
        
        # Get the hashed_master_secret
        hashed_password = hash_secret(password, salt=salt)

        # Check if the hashed password matches the one in the database
        if hashed_password['secret_hash'] == master_secret_hash:
            return True
        else:
            return False
        
    except Exception as e:
        logger.error(f"Error occured checking user: {username}'s password. {e}")



def authenticate_user(data):
    """
    Check user's username and password.

    Args:
        data (JSON): The username and password of the user.

    Returns:
        tuple: A tuple with the  
    """

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data:

        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username and password are required."
        }), 400
    
    # Get username and password from the data
    username = data['username']
    password = data['password']
    
    # Check if user exists in vadafi-users database
    if not user_exists(username):
        
        # Return unauthorized if user does not exist
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid username or password."
        }), 401

    # Check if password is correct
    if not check_password(password, username):
        
        # Return unauthorized if password is wrong
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid username or password."
        }), 401

    # Authentication succesful
    return True, username




