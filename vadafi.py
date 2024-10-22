# vadafi.py

import os
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from pathlib import Path
from dotenv import load_dotenv
 
from modules.tools.authentication import authenticate_user
from modules.tools.logger import vadafi_logger

logger = vadafi_logger()

# Load the env variables
env_path = Path('.env')
load_dotenv(env_path)

# Initialize flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Set jwt secret
app.config['JWT_SECRET_KEY'] = os.getenv('API_SECRET')
jwt = JWTManager(app)


@app.route('/')
def home():
    return render_template('index.html')

# Route for requesting JWT token
@app.route('/get_token', methods=['POST'])
def get_token():
    
    try:
        # Get data from request
        data = request.get_json()

        # Authenticate user
        response, username = authenticate_user(data)
        # No or faulty data has been posted
        if response == None:
            return jsonify({
                "error": "Bad request",
                "message": "Username and password are required."
            }), 400

        # Username or password is wrong
        if not response: 
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid username."
            }), 401

        # Authentication is succesful
        if response:
            # Create access token
            access_token = create_access_token(identity=username)

            return jsonify({
                "message": "Authentication succesful",
                "jwt": access_token,
                "username": username
                }), 200

    except Exception as e:
        logger.error(f"Error occured while trying to respond. {e}")

if __name__ == '__main__':
    app.run()

