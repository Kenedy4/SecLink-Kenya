import React, { useState } from "react";

function Footer() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Message sent successfully!");
  };

  return (
    <footer>
      <div className = "form-group">
      <h2>Contact Us</h2>
      <form onSubmit={handleSubmit}>
        <label>Name: </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <label>Email: </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label>Message: </label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
        ></textarea>

        <button type="submit">Send Message</button>
      </form> </div>
      
      <div class="social-media">
        <a href="https://www.facebook.com/seclinkkenya/" class="fab fa-facebook">
        Follow us on Facebook 
        </a>
        <a href="https://www.instagram.com/seclinkkenya/" class="fab fa-instagram">
          Follow us on Instagram
        </a>
        <a href="https://twitter.com/seclinkkenya/" class="fab fa-twitter">
          Follow us on Twitter
        </a>
        <a href="https://www.linkedin.com/company/seclink-kenya/" class="fab fa-linkedin">
          Follow us on LinkedIn
        </a>
      </div>
      <p> &copy; 2024 SecLink Kenya. All rights reserved.</p>

    </footer>
  );
}

export default Footer;
