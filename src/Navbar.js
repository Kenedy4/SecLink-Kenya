import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';  // For Navbar component
import './Login.css';   // For Login component
import './Dashboard.css';  // For dashboard components
function Navbar() {
  return (
    <nav>
      <ul>
        <li><Link to="/">Login</Link></li>
        <li><Link to="/student-dashboard">Student Dashboard</Link></li>
        <li><Link to="/parent-dashboard">Parent Dashboard</Link></li>
        <li><Link to="/teacher-dashboard">Teacher Dashboard</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
