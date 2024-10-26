import React from 'react';
import './Homepage.css'; // For custom styling (create this file)

const Homepage = () => {
    return (
        <div className="homepage">
            <header className="homepage-header">
                <h1>Welcome to Vadafi</h1>
                <p>Your secure secret manager solution.</p>
            </header>
            <main className="homepage-main">
                <section className="about-section">
                    <h2>About Vadafi</h2>
                    <p>
                        Vadafi helps you securely store and manage your secrets. 
                        With our user-friendly interface and robust backend, you can 
                        keep your sensitive information safe and accessible.
                    </p>
                </section>
                <section className="features-section">
                    <h2>Features</h2>
                    <ul>
                        <li>Secure secret storage</li>
                        <li>User-specific access management</li>
                        <li>Simple integration with your existing workflows</li>
                    </ul>
                </section>
            </main>
        </div>
    );
};

export default Homepage;

