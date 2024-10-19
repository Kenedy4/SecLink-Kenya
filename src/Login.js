import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';  // For Navbar component
import './Login.css';   // For Login component
import './Dashboard.css';  // For dashboard components
function Login() {
  const [role, setRole] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (role === 'student') {
      navigate('/student-dashboard');
    } else if (role === 'parent') {
      navigate('/parent-dashboard');
    } else if (role === 'teacher') {
      navigate('/teacher-dashboard');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <label htmlFor="role">Select Role: </label>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">--Select Role--</option>
          <option value="student">Student</option>
          <option value="parent">Parent</option>
          <option value="teacher">Teacher</option>
        </select>
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
