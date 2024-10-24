# secrets.py

from .tools.encryption import encrypt_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger
from .tools.authentication import get_user_dbconfig
from flask import jsonify

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



def list_secrets(username, master_secret):
    """
    List all secrets in the database.

    Args:
        username (str): Username.
        master_secret (str): The user's master secret.
    """

    # Create user credentials dict
    credentials = {
        'dbname': username,
        'user': username,
        'password': master_secret,
        'host': "localhost",
        'port': 5432
        }

    try:
        # Add secret to database
        result = execute_query(f"select id, name from secrets;", return_data=True, credentials=credentials)
        logger.info(f"Fetched all secrets in table: secrets on database: {username} of user: {username}.")

        return result

    except Exception as e:
        logger.error(f"Error occured while trying to list secrets in table secrets on database {username} of user {username}. {e}")
        return False



def reveal_secret(credentials, secret_name):
    """
    Reveal a secret.

    Args:
        credentials (dict): A dictionary with the user's credentials.
        secret_name (str): The name of the secret to be revealed.

    Returns:
        plain_text_secret (str): The secret in plain text.
    """


