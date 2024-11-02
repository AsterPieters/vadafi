# users.py

import re
from flask import jsonify

from .tools.encryption import hash_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger
from .tools.authentication import get_admin_dbconfig
from .tools.authentication import get_user_id
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



def create_user(username, password):
    """
    Creates a user, hashes the secret, and stores the information in the database.

    Args:
        username (STR): The user's username.
        password (STR): The user's password.

    Returns:
        bool: True if created succesfully.
    """


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

        

        return jsonify({
            "message": "User created succesfully."
        }), 200

