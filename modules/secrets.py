# secrets.py


from .tools.encryption import encrypt_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger

logger = vadafi_logger()


def add_secret(username, master_secret, secret_name, plain_text_secret):
    """
    Encrypt and add secret to the database.

    Args:
        username (str): Username.
        master_secret (str): The user's master secret.
        secret_name (str): The name of the secret.
        plain_text_secret (str): The secret in clear text.
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
        # Encrypt the secret
        secret_data = encrypt_secret(master_secret, plain_text_secret)

        # Create the query
        query = """
        INSERT INTO secrets (name, secret, salt, iv)
        VALUES (%s, %s, %s, %s)
        """

        # Set the params
        params = (
            secret_name, 
            secret_data["secret"], 
            secret_data["salt"], 
            secret_data["iv"]
            )

        # Add secret to database
        execute_query (query, params=params, credentials=credentials)
        logger.info(f"Added secret: {secret_name} to table: secrets on database: {username} for user: {username}.")

        return True

    except Exception as e:
        logger.error(f"Error occurred while trying to add secret: {secret_name} to database: {username}. {e}")
        return False



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


