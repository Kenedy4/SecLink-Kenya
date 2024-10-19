import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <ul>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/learning-materials">Learning Materials</Link></li>
        <li><Link to="/profile">Profile</Link></li>
        <li><Link to="/reports">Reports</Link></li>
        <li><Link to="/notifications">Notifications</Link></li>
        <li><Link to="/logout">Logout</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;
