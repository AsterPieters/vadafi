# users.py

import re

from tools.authentication import get_admin_dbconfig
from .tools.execute_query import execute_query  
from .tools.logger import vadafi_logger

logger = vadafi_logger()


def check_username_validity(username):
    """
    Check if username is valid.
    """
    return re.match("^[a-zA-Z0-9_]{1,30}$", username) is not None



def check_username_availability(username):
    """
    Check if username is available in the vadafi_users table.
    """
    try:
        # Get the dbconfig
        dbconfig = get_admin_dbconfig()

        # Create the query
        query = """
        SELECT COUNT(*) FROM vadafi_users WHERE username = %s
        """
        result = execute_query(
            query,
            params=(username,),
            return_data=True,
            dbconfig=dbconfig
            )
        if result[0][0] == 0:
            return True
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error occured while checking username availability. {e}")
        return False

