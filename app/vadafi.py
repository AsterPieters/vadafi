# vadafi.py

import os
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
 
from modules.tools.authentication import authenticate_user
from modules.tools.logger import vadafi_logger
from modules.users import create_user
from modules.secrets import add_secret, fetch_secrets, reveal_secret

logger = vadafi_logger()

# Load the env variables
env_path = Path('.env')
load_dotenv(env_path)

# Initialize flask
app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')

# Set jwt secret
app.config['JWT_SECRET_KEY'] = os.getenv('API_SECRET')
jwt = JWTManager(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return "This is the about page!"

# Route for creating user
@app.route('/create_user', methods=['POST'])
def create_user_api():

    # Get data from request
    data = request.get_json()

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data:
        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username and password are required."
        }), 400

    # Get data from dict
    username = data['username']
    password = data['password']
    
    # Create user
    result = create_user(username, password)

    # Check output for result
    return result



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



@app.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    # Get the username
    current_user = get_jwt_identity()

    return jsonify({
        'message': 'Access granted',
        'user': current_user
    }), 200




@app.route('/add_secret', methods=['POST'])
@jwt_required()
def add_secret_api():
    # Get the data
    data = request.get_json()

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data or 'secret_name' not in data or 'plain_text_secret' not in data:
        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username, password, secret_name, plain_text_secret are required."
        }), 400

    # Get the data from dict
    username = data['username']
    password = data['password']
    secret_name = data['secret_name']
    plain_text_secret = data['plain_text_secret']

    # Add secret
    result = add_secret(
            username,
            password,
            secret_name,
            plain_text_secret
        )

    return result


@app.route('/fetch_secrets', methods=['GET'])
@jwt_required()
def fetch_secrets_api():
    # Get the data
    data = request.get_json()

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data:
        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username and password are required."
        }), 400

    # Get the data from the dict
    username = data['username']
    password = data['password']

    result = fetch_secrets(username, password) 
    
    return result



@app.route('/reveal_secret', methods=['GET'])
@jwt_required()
def reveal_secret_api():
    # Get the data
    data = request.get_json()

    # Check if al data is provided
    if not data or 'username' not in data or 'password' not in data or 'secret_name' not in data:
        # Return bad request if not
        return jsonify({
            "error": "Bad request",
            "message": "Username, password and secret_name are required."
        }), 400

    # Get the data from the dict
    username = data['username']
    password = data['password']
    secret_name = data['secret_name']

    # Reveal the secret
    result = reveal_secret(username, password, secret_name) 
    
    return result


if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=5000))

