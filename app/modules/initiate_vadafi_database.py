# initiate_vadafi_database.py

from tools.logger import vadafi_logger
from tools.execute_query import execute_query, get_admin_dbconfig

logger = vadafi_logger()

# Create user database
query = """
    CREATE TABLE vadafi_users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        master_secret_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
try:

    # Get admin dbconfig
    dbconfig = get_admin_dbconfig()

    execute_query(
            query,
            dbconfig=dbconfig
            )
    logger.info("Created table vadafi_users.")

except Exception as e:
    logger.error(f"Error occured while trying to initiate vadafi database: {e}")
