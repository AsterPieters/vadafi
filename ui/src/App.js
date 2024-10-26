import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Homepage from './components/Homepage';
import Signuppage from './components/Signuppage';
import Loginpage from './components/Loginpage';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <nav>
                    <ul>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/signup">Sign Up</Link></li>
                        <li><Link to="/loginpage">Log In</Link></li>
                    </ul>
                </nav>
                <Routes>
                    <Route path="/" element={<Homepage />} />
                    <Route path="/signup" element={<Signuppage />} />
                    <Route path="/loginpage" element={<Loginpage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
