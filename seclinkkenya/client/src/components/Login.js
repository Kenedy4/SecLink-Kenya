import React, { useState } from 'react';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5555/login', { username, password })
      .then((response) => {
        setToken(response.data.token);
        localStorage.setItem('token', response.data.token); // Store token
        alert('Login successful');
      })
      .catch((error) => {
        alert(error.response.data.error || 'Error logging in');
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <label>Username: </label>
      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />

      <label>Password: </label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

      <button type="submit">Login</button>
    </form>
  );
}

export default Login;
