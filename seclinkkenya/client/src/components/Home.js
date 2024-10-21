import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      <Navbar />
      <h1>Welcome SecLink Kenya</h1>
   
    </div>
  );
}

function Navbar() {
  return (
    <nav>
      <ul className="navbar">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/signup">Signup</Link></li>
        <li><Link to="/login">Login</Link></li>
        <li><Link to="/about">About Us</Link></li>
        <li><Link to="/contactus">Contact Us</Link></li>
      </ul>
    </nav>
  );
}

export default Home;
