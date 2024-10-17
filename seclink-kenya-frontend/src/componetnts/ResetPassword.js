import React, { useState } from 'react';
import axios from 'axios';

const ResetPassword = () => {
  const [email, setEmail] = useState('');

  const handleReset = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/reset-password', { email });
      alert('Password reset link sent!');
    } catch (error) {
      console.error('Error sending reset link', error);
    }
  };

  return (
    <div className="reset-container">
      <h2>Reset Password</h2>
      <form onSubmit={handleReset}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
        />
        <button type="submit">Send Reset Link</button>
      </form>
    </div>
  );
};

export default ResetPassword;
