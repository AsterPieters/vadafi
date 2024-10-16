# create_user_db.py

import sys
import os

# Set path to tools
tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools'))
sys.path.append(tools_path)

from execute_query import execute_query

# Create user database
query = """
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

execute_query(query, False)
