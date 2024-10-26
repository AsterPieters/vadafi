import React, { useState } from 'react'
import './Loginpage.css';

function LogIn() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [responseMessage, setResponseMessage] = useState('');

    const handleLogIn = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://127.0.0.1:5000/get_jwt_token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            });

            if (response.ok) {
                const result = await response.json();
                setResponseMessage(result.message); // Set the message from the API
            } else {
                const errorResult = await response.json();
                setResponseMessage(errorResult.message);
            }
        } catch (error) {
            setResponseMessage('An error occured while logging in.');
            console.error('Error occurred while logging in:', error);
        }
    };


    return (
        <div className="login-container">
            <h2>Log In</h2>
            <form onSubmit={handleLogIn} className="login-form">
                <div className="form-group">
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="login-button">Log In</button>
            </form>
            {responseMessage && (
                <div className="response-message">
                    {responseMessage}
                </div>
            )}
        </div>
    );
}

export default LogIn;


