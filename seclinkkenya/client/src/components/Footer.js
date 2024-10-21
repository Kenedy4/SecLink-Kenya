import React, { useState } from 'react';

function Footer() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Message sent successfully!');
  };

  return (
    <footer>
      <h2>Contact Us</h2>
      <form onSubmit={handleSubmit}>
        <label>Name: </label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />

        <label>Email: </label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

        <label>Message: </label>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} required></textarea>

        <button type="submit">Send Message</button>
      </form>
    </footer>
  );
}

export default Footer;
