import React, { useState } from "react";
import axios from "axios";

function ContactUs() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const contactData = {
      name: name,
      email: email,
      message: message,
    };

    axios
      .post("https://seclink-kenya.onrender.com/contact", contactData)
      .then((response) => {
        alert("Message sent successfully!");
        setName("");
        setEmail("");
        setMessage("");
      })
      .catch((error) => {
        alert("Error sending message");
      });
  };

  return (
    <div className="card contactus-card">
      <form onSubmit={handleSubmit}>
        <h2>Contact Us</h2>
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
      </form>
    </div>
  );
}

export default ContactUs;
