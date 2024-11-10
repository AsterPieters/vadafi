# user.py

import os
from dotenv import load_dotenv
from pathlib import Path
from flask import jsonify
from werkzeug.wrappers import response

from .tools.encryption import hash_secret
from .tools.execute_query import execute_query
from .tools.execute_query import get_admin_dbconfig
from .tools.logger import vadafi_logger
from .tools.authentication import user_exists
from .users import check_username_validity, check_username_availability
logger = vadafi_logger()

class User:
    
    # Initialize the user
    def __init__(self, username, master_password, create=False):

        # Check user existence
        if user_exists(username):
            self.load_info(username, master_password)
        else:
            # Create new user
            if create:
                self.username = username
                self.master_password = master_password
                self.create_vadafi_user()
            
            else:
                #TODO: handle wrong Username
                pass



    def load_info(self, username, master_password):
        """
        Load user info from database.
        """
        self.username = username
        self.master_password = master_password
        self.user_id = self.get_id()
        self.db_name = f"db_{self.user_id}"
        self.db_user_name = f"user_{self.user_id}"
        self.dbconfig = self.get_dbconfig()
        


    def create_vadafi_user(self):
        """
        Create user database and database user.
        """
        
        # Create user and database
        success, response = self.create_user(dklfjklasdjflk;asdjflksdjfl;asdjflkasdjfklasdfjl;nvvvvhvhvhv ghjffhja;lakdjfklasdlfjdkasjflkdjf;asdjklveree
        if not success:
            return response
        success, response = self.create_database()
        if not success:
            return response


        return jsonify({
            "message": f"User {self.username} and database created successfully."
        }), 201




    def create_user(self):
        """
        Create the user in the vadafi_user table and database.
        """
        try:
            # Check if username is valid
            if check_username_validity(username):
                pass
            else:
                # Return username not valid
                return False, jsonify({
                    "error": "Username not valid",
                    "message": "Sorry, this username is not valid."
                }), 200

            # Check if username is available
            if check_username_availability(username):
                pass
            else:
                # Return username not available
                return False, jsonify({
                    "error": "Username unavailable",
                    "message": "Sorry, this username is not available."
                }), 200

            # Get the dbconfig for the vadafi database
            vadafi_dbconfig = get_admin_dbconfig()

            # Hash the master password and get the values
            hashed_data = hash_secret(master_password)
            hashed_master_password = hashed_data["secret_hash"]
            salt = hashed_data["salt"]

            # Add user to vadafi_users
            query="""
            INSERT INTO vadafi_users (username, master_secret_hash, salt)
            VALUES (%s, %s, %s)
            """
            execute_query(
                query,
                params=(username, hashed_master_password, salt),
                dbconfig=vadafi_dbconfig
                )
           
            self.load_info(username, master_password)

            # Success
            logger.info(f"Created user {username} in vadafi_users table.")
            return True, None
        

        except Exception as e:
            logger.error(f"Error occured while trying to create user {self.username} in vadafi database {e}")
            return False, jsonify({
                "error": "User creation error",
                "message": "Sorry, we could not create your user at this moment."
            }), 500



    def create_database(self):
        """
        Create the user's database and 'secrets' table.
        """
        try:
            # Get the admin dbconfig
            admin_dbconfig = get_admin_dbconfig()
            user_admin_dbconfig = get_admin_dbconfig(dbname=self.db_name)

            # Create database
            execute_query(
                f"CREATE DATABASE {self.db_name}",
                autocommit=True,
                dbconfig=admin_dbconfig
                )
            logger.info(f"Created {self.db_name}.")

            # Create database user
            execute_query(
                f"CREATE USER {self.db_user_name} WITH PASSWORD %s",
                params=(self.master_password,),
                dbconfig=admin_dbconfig
                )
            logger.info(f"Created {self.db_user_name}.")

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
                    dbconfig=user_admin_dbconfig
                    )
            logger.info(f"Created table 'secrets' on {self.db_name}.")

            # Configure the user's privileges
            execute_query(f"ALTER DATABASE {self.db_name} OWNER TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"ALTER SCHEMA public OWNER TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"GRANT USAGE, CREATE ON SCHEMA public TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"ALTER TABLE public.secrets OWNER TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            execute_query(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {self.db_user_name};", dbconfig=user_admin_dbconfig)
            logger.info(f"Configured privileges for {self.db_user_name} in database {self.db_name}.")

            # Success
            logger.info(f"Granted permissions on {self.db_name} for user {self.db_user_name}.")
            return True, None


        except Exception as e:
            logger.error(f"Error occured while trying to create database/(user/) with id {self.user_id} {e}")
            
            # Return error
            return False, jsonify({
                "error": "Error occured creating database",
                "message": "Sorry, we could not create your database at this moment."
            }), 400



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
           params=(self.username, ),
           return_data=True,
           dbconfig=dbconfig
            )
        if result:
            return result[0][0]
        else:
            return None



    def get_dbconfig(self):
        """
        Get the dbconfig of the user.
        """    
     
        # Load the .env file into the environment variables
        env_path = Path('.env')
        load_dotenv(env_path)

        # Put the credentials into the dbconfig dict
        dbconfig = {
        'dbname': self.db_name,
        'user': self.db_user_name,
        'password': self.master_password,
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
            }
       
        return dbconfig
