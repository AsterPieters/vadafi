# initiate_vadafi_database.py

from tools.execute_query import execute_query

# Create user database
query = """
    CREATE TABLE vadafi_users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

execute_query(query, False)
