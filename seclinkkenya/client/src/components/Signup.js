import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

function Signup() {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("teacher"); // Default role is 'Teacher'
  const [loading, setLoading] = useState(false);
  const [signupSuccess, setSignupSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");

    // Prepare data payload for the API
    const payload = {
      username,
      name,
      email,
      password,
      role,
      subject: role === "teacher" ? subject : undefined, // Send subject only if role is teacher
    };

    axios
      .post("https://seclink-server.onrender.com/signup", payload)
      .then((response) => {
        setSignupSuccess(true);
        setLoading(false);
        setTimeout(() => navigate("/login"), 2000);
      })
      .catch((error) => {
        setLoading(false);
        setErrorMessage(error.response?.data?.message || "Error signing up");
      });
  };

  return (
    <div className="card signup-card">
      <form onSubmit={handleSubmit}>
        <h2>Sign Up</h2>

        {errorMessage && <p className="error-message">{errorMessage}</p>}

        <label>Username: </label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label>Email: </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label>Name: </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        {role === "teacher" && (  // Conditionally render subject field for teachers
          <>
            <label>Subject: </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required={role === "teacher"}  // Subject is required for teacher
            />
          </>
        )}

        <label>Password: </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <label>Role: </label>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="teacher">Teacher</option>
          <option value="parent">Parent</option>
        </select>

        <button type="submit" disabled={loading}>
          {loading ? "Signing Up..." : "Sign Up"}
        </button>

        {signupSuccess && (
          <div className="success-message">
            <p>Signup successful! Redirecting to login...</p>
          </div>
        )}
      </form>
      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}

export default Signup;
