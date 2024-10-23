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
@app.route('/get_jwt_token', methods=['POST'])
def get_jwt_token_api():
    
    # Get data from request
    data = request.get_json()

    # Check username and password
    auth_result = authenticate_user(data)

    # Check output for result
    if not isinstance(auth_result, tuple):
        return jsonify({"error": "Internal Server Error", "message": "Unexpected response from authentication"}), 500
    if auth_result[0] is not True:
        return auth_result

    # Create access token
    username = auth_result[1]
    access_token = create_access_token(identity=username)

    # Return the jwt token
    return jsonify({
        "message": "Authentication succesful",
        "jwt": access_token,
        "username": username
        }), 200

# Route for creating user
@app.route('/create_user', methods=['POST'])
def create_user_api():
    print("test")

if __name__ == '__main__':
    app.run()

