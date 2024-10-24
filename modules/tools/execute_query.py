# execute_query.py

import psycopg2
from psycopg2 import OperationalError, DatabaseError

from .logger import vadafi_logger

logger = vadafi_logger()

def execute_query(query, return_data=False, params=None, autocommit=False, dbconfig=None):
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

    # Initialize connection
    connection = None
    cursor = None
    results = []

    try:
        # Connect to the Database
        connection = psycopg2.connect(**dbconfig)
        
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
        raise

    except DatabaseError as e:
        logger.error(f"Database error occured while executing query: {e}")
        return False

    finally:
        # Close the connection safely
        if 'cursor' in locals() and cursor:
            cursor.close()
        
        if 'connection' in locals() and connection:
            connection.close() 

    # Return data or empty list
    if return_data:
        return results 
    else:
        return True
