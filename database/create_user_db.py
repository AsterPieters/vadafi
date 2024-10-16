# create_user_db.py

import sys
import os

# Get the relative path to the tools directory
tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools'))

# Add the tools directory to the system path
sys.path.append(tools_path)

# Now you can import execute_query
from execute_query import execute_query



query = """
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,  -- If using a salt separately
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

result = execute_query(query, False)
print(result)
