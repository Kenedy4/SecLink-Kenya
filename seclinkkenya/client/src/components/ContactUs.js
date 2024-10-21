import React from 'react';

function ContactUs() {
  const scrollToFooter = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    });
  };

  return (
    <div>
      <h2>Contact Us</h2>
      <p>If you have any questions, please fill out the contact form below.</p>
      <button onClick={scrollToFooter}>Go to Contact Form</button>
    </div>
  );
}

export default ContactUs;
