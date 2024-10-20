# execute_query.py

import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import sys
import os


from psycopg2 import OperationalError, DatabaseError
from .logger import vadafi_logger

logger = vadafi_logger()

def load_admin_credentials():
    # Load database credentails into the env variables
    env_path = Path('.env')
    load_dotenv(env_path)

    # Get the database credentials out of the env variables
    credentials = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
            }

    return credentials



def execute_query(query, return_data=False, params=None, autocommit=False, credentials=None):
    """
    Executes a query on the vadafi database.

    Args:
        query (str): The query to execute.
        return_data (bool): Should the query return data.
        params (str): Parameters for the query, we use this to counter SQL injection.
        autocommit (bool): Set the connection mode to autocommit.
        credentials (dict): Database credentials.

    Returns:
        list: Returns data if return_data is True.

    Raises:
        Exception: If a database error occurs.
    """

    # Load the admin creds if no provided
    if not credentials:
        credentials = load_admin_credentials()

    # Initialize connection
    connection = None
    cursor = None
    results = []

    try:
        # Connect to the Database
        connection = psycopg2.connect(**credentials)
        
        # Enable autocommit if True
        if autocommit:
            connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        # Initialize cursor
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query, params)

        # Fetch data if needed
        if return_data:
            results = cursor.fetchall()

        # Commit change
        if not autocommit:
            connection.commit()

    # Except database issues
    # We except other issues later
    # Exit the program if the database has issues
    except OperationalError as e:
        logger.error(f"Operational error occured while executing query: {e}")
        sys.exit()

    except DatabaseError as e:
        logger.error(f"Database error occured while executing query: {e}")

    finally:
        # Close the connection safely
        if 'cursor' in locals() and cursor:
            cursor.close()
        
        if 'connection' in locals() and connection:
            connection.close() 

    # Return data or empty list
    if return_data:
        return results

