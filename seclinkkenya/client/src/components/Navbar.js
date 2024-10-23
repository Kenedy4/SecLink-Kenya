// src/components/Navbar.js

import React from 'react';
import { Link } from 'react-router-dom';

function Navbar({ scrollToContact }) {
  return (
    <nav>
      <ul className="navbar">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/about">About Us</Link></li>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/signup">Signup</Link></li>
        <li><Link to="/login">Login</Link></li>
       
        <li><Link to="#" onClick={scrollToContact}>Contact Us</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
