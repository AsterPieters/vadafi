# execute_query.py

import psycopg2
import os

from psycopg2 import sql, OperationalError, DatabaseError
from dotenv import load_dotenv
from pathlib import Path


def execute_query(query, return_data=False):
    """
    Executes a query on the Postgres database.

    Args:
        query (str): The query to execute.
        return_data (bool): Should the query return data.
    
    Returns:
        list: Returns data if return_data is True.

    Raises:
        Exception: If a database error occurs.
    """

    # Load database credentails
    env_path = Path(f'./.env_vadafi')
    load_dotenv(env_path)

    # Get the database credentials out of the env variables
    db_config = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
            }

    # Initialize connection
    connection = None
    results = []

    try:
        # Connect to the Database
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch data if needed
        if return_data:
            results = cursor.fetchall()

        # Commit change
        connection.commit()

    except (OperationalError, DatabaseError) as e:
        print(f"Database error: {e}")
        raise
    
    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    # Return data or empty list
    return results
