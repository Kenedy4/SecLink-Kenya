import React from 'react';
import './Navbar.css';  // For Navbar component
import './Login.css';   // For Login component
import './Dashboard.css';  // For dashboard components
function ParentDashboard() {
  return (
    <div>
      <h2>Parent Dashboard</h2>
      <p>View notifications about your child’s progress.</p>
      {/* Add notification and updates list here */}
    </div>
  );
}

export default ParentDashboard;
