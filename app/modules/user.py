# user.py

import re
from flask import jsonify

from .tools.encryption import hash_secret
from .tools.execute_query import execute_query
from .tools.logger import vadafi_logger
from .tools.authentication import get_admin_dbconfig
from .tools.authentication import get_user_id
logger = vadafi_logger()

class User:
    
    # Initialize the user
    def __init__(self, username, master_password):
        self.username = username
        self.master_password = master_password



    def create_user(self):
        """
        Create the user in the vadafi_user table and database.
        """
        try:
            # Get the dbconfig for the vadafi database
            vadafi_dbconfig = get_admin_dbconfig()

            # Hash the master password and get the values
            hashed_data = hash_secret(self.master_password)
            self.hashed_master_password = hashed_data["secret_hash"]
            self.salt = hashed_data["salt"]

            # Add user to vadafi_users
            query="""
            INSERT INTO vadafi_users (username, master_secret_hash, salt)
            VALUES (%s, %s, %s)
            """
            execute_query(
                query,
                params=(self.username,),
                dbconfig=vadafi_dbconfig
                )
            logger.info(f"Created user {self.username} in vadafi_users table.")
        
            # Name database & database_user based on user's unique identifier
            self.user_id = get_user_id(self.username) 
            self.db_name = f"db_{self.user_id}"
            self.db_user_name = f"user_{self.user_id}"

        except Exception as e:
            logger.error(f"Error occured while trying to create user {username} in vadafi database {e}")
        
        # Return error
        return jsonify({
            "error": "Error occured creating user",
            "message": "Sorry, we could not create your user at this moment."
        }), 400



    def create_database(self):
        try:
            # Create database
            execute_query(
                f"CREATE DATABASE {db_name}",
                autocommit=True,
                dbconfig=vadafi_dbconfig
                )
            logger.info(f"Created {db_name}.")

            # Create database user
            execute_query(
                f"CREATE USER {db_user_name} WITH PASSWORD %s",
                params=(password,),
                dbconfig=vadafi_dbconfig
                )
            logger.info(f"Created {db_user_name}.")

            # Create secret table
            query = """
            CREATE TABLE secrets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                secret TEXT NOT NULL,
                salt VARCHAR(255) NOT NULL,
                iv VARCHAR(255) NOT NULL
            );
            """
            execute_query(
                    query, 
                    dbconfig=user_dbconfig
                    )
            logger.info(f"Created table 'secrets' on {db_name}.")

            # Configure the user's privileges
            execute_query(f"ALTER DATABASE {db_name} OWNER TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"ALTER SCHEMA public OWNER TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"GRANT USAGE, CREATE ON SCHEMA public TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"ALTER TABLE public.secrets OWNER TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user_name};", dbconfig=user_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {db_user_name};", dbconfig=user_dbconfig)
            logger.info(f"Configured privileges for {db_user_name} in database {db_name}.")

            # Log the success
            logger.info(f"Succesfully created user {username}!")

        except Exception as e:
            logger.error(f"Error occured while trying to create user {username} in vadafi database {e}")



        def get_id(self):
            """
            Get the unique identifier of the user.
            """

            # Get the dbconfig
            dbconfig = get_admin_dbconfig()    

            # Create the query
            query="""
            SELECT user_id FROM vadafi_users WHERE username = %s
            """

            # Get the user_id
            result = execute_query(
               query,
               params=(username, ),
               return_data=True,
               dbconfig=dbconfig
                )
            if result:
                return result[0][0]
            else:
                return None



            # Get the dbconfig for the user database
            # This will also be as the admin
            user_dbconfig = get_admin_dbconfig(self.db_name)
