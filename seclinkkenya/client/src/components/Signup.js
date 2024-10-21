import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Signup() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('teacher');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5555/signup', { username, password, role })
      .then((response) => {
        alert(response.data.message);
        navigate('/login');  // Redirect to login after signup
      })
      .catch((error) => {
        alert(error.response.data.message || 'Error signing up');
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Signup</h2>
      <label>Username: </label>
      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
      
      <label>Password: </label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      
      <label>Role: </label>
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="teacher">Teacher</option>
        <option value="parent">Parent</option>
      </select>
      
      <button type="submit">Sign Up</button>
    </form>
  );
}

export default Signup;
