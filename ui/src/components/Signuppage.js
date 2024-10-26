import React, { useState } from 'react'
import './Signuppage.css';

function SignUp() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [responseMessage, setResponseMessage] = useState('');

    const handleSignUp = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://127.0.0.1:5000/create_user', {
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
                console.log('User created successfully:', result);
                // Handle successful user creation (e.g., redirect or show a success message)
            } else {
                const errorResult = await response.json();
                setResponseMessage(errorResult.message);
                console.error('Failed to create user:', errorResult);
                // Handle error (e.g., show an error message)
            }
        } catch (error) {
            setResponseMessage('An error occured while signing up.');
            console.error('Error occurred while signing up:', error);
            // Handle network error (e.g., show an error message)
        }
    };


    return (
        <div className="signup-container">
            <h2>Sign Up</h2>
            <form onSubmit={handleSignUp} className="signup-form">
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
                <button type="submit" className="signup-button">Sign Up</button>
            </form>
            {responseMessage && (
                <div className="response-message">
                    {responseMessage}
                </div>
            )}
        </div>
    );
}

export default SignUp;

