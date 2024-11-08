# secrets.py

from flask import jsonify

from .tools.encryption import encrypt_secret, decrypt_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger

logger = vadafi_logger()

def check_secret_availability(username, password, secret_name):
    """
    Check if secret_name is available in the user's secrets table.
    """
    try:
        # Get the dbconfig
        dbconfig = get_user_dbconfig(username, password)

        # Create the query
        query = """
        SELECT COUNT(*) FROM secrets WHERE name = %s
        """
        result = execute_query(
            query,
            params=(secret_name,),
            return_data=True,
            dbconfig=dbconfig
            )
        if result[0][0] == 0:
            return True
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error occured while checking secret name availability.")
        return False



def check_secret_existance(username, password, secret_name):
    """
    Check if secret exists in the user's secrets table.
    """
    try:
        # Get the dbconfig
        dbconfig = get_user_dbconfig(username, password)

        # Create the query
        query = """
        SELECT COUNT(*) FROM secrets WHERE name = %s
        """
        result = execute_query(
            query,
            params=(secret_name,),
            return_data=True,
            dbconfig=dbconfig
            )
        if result[0][0] == 0:
            return False
        else:
            return True
    
    except Exception as e:
        logger.error(f"Error occured while checking secret existance. {e}")
        return False



def add_secret(username, password, secret_name, plain_text_secret):
    """
    Encrypt and add secret to the database.

    Args:
        username (str): The user's username.
        password (str): The user's password.
        secret_name (str): The name of the secret.
        plain_text_secret (str): The secret in clear text.
    """

    if check_secret_availability(username, password, secret_name):
        pass
    else:
        # Return secret name not valid
        return jsonify({
            "error": "Secret name not available",
            "message": "Sorry, this secret name is not available."
        }), 200       


    # Create dbconfig
    dbconfig = get_user_dbconfig(username, password)

    try:
        # Encrypt the secret
        secret_data = encrypt_secret(password, plain_text_secret)

        # Create the query
        query = """
        INSERT INTO secrets (name, secret, salt, iv)
        VALUES (%s, %s, %s, %s)
        """

        # Add the secret to the database
        execute_query(
            query,
            params=(secret_name, secret_data["secret"], secret_data["salt"], secret_data["iv"]),
            dbconfig=dbconfig
        )
        logger.info(f"Added secret {secret_name} for user {username}.")

        return jsonify({
            "message": "Secret created succesfully."
        }), 200

    except Exception as e:
        logger.error(f"Error occurred while trying to add secret {secret_name} for user {username}. {e}")

        return jsonify({
            "error": "Error occured while adding secret",
            "message": "Sorry, we could not add your secret at this moment."
        }), 400



def fetch_secrets(username, password):
    """
    Fetch secrets in the user's secrets table.

    Args:
        username (str): The user's username.
        password (str): The user's password.

    Return:
        result (JSON): The user's secret_id's and secret_names.
    """
    try:
        # Get the dbconfig
        dbconfig = get_user_dbconfig(username, password)

        # Fetch secrets
        result = execute_query(
            f"SELECT id, name FROM secrets;", 
            return_data=True,
            dbconfig=dbconfig
            )
        logger.info(f"Fetched secrets of user {username}.")

        return jsonify({
            "message": "Fetched secrets succesfully.",
            "data": result
            }), 200

    except Exception as e:
        logger.error(f"Error occured while trying to fetch secrets for user {username}. {e}")
        
        return jsonify({
            "error": "Error occured while fetching secrets",
            "message": "Sorry, we could not fetch your secrets at this moment."
            }), 400



def reveal_secret(username, password, secret_name):
    """
    Reveal a secret.

    Args:
        username (STR): The user's username.
        password (STR): The user's password.
        secret_name (STR): The to be revealed secret.

    Returns:
        plain_text_secret (str): The revealed secret in plain text.
    """
    try:
        # Get the dbconfig
        dbconfig = get_user_dbconfig(username, password)

        if check_secret_existance(username, password, secret_name):
            pass
        else:
            # Return secret not found
            return jsonify({
                "error": "Secret not found",
                "message": "Sorry, this secret could not be found."
            }), 200

        # Create the query
        query = """
        SELECT secret, salt, iv FROM secrets WHERE name = %s
        """
        result = execute_query(
            query,
            params=(secret_name,),
            return_data=True,
            dbconfig=dbconfig
            )

        # Get the data
        secret_data = {
            'secret': result[0][0],
            'salt': result[0][1],
            'iv': result[0][2]
            }

        # Decrypt the secret
        plain_text_secret = decrypt_secret(password, secret_data)

        return jsonify({
            "message": "Revealed secret succesfully.",
            "data": plain_text_secret
            }), 200

    except Exception as e:
        logger.error(f"Error occured while revealing secret {secret_name} for user {username}. {e}")
        
        return jsonify({
            "error": "Error occured while fetching secrets",
            "message": "Sorry, we could not fetch your secret at this moment."
            }), 400


