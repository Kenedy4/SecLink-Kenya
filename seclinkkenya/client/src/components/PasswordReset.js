import React, { useState } from 'react';
import axios from 'axios';

function PasswordReset() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5555/password-reset-request', { email })
      .then((response) => {
        alert(response.data.message);
      })
      .catch((error) => {
        alert(error.response.data.message || 'Error sending password reset link');
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Password Reset</h2>
      <label>Email: </label>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

      <button type="submit">Send Reset Link</button>
    </form>
  );
}

export default PasswordReset;
