import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

function Auth() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resetMode, setResetMode] = useState(false);
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false); // To track button state
  const [errorMessage, setErrorMessage] = useState(""); // For inline error handling
  const navigate = useNavigate();

  // Login function
  const handleLoginSubmit = (e) => {
    e.preventDefault();
    setLoading(true); // Disable button and show loading state
    setErrorMessage(""); // Clear error messages

    axios
      .post("http://localhost:5555/login", { username, password })
      .then((response) => {
        console.log(response)
        const token = response.data.token; // Ensure you use access_token from response
        localStorage.setItem("token", token); // Store the token in localStorage
        localStorage.setItem("role", response.data.role); // Store the token in localStorage

        setLoading(false);
        navigate("/dashboard"); // Redirect to dashboard
      })
      .catch((error) => {
        setLoading(false);
        setErrorMessage(error.response?.data?.error || "Error logging in");
      });
  };

  // Password reset function
  const handlePasswordResetSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");

    axios
      .post("http://localhost:5555/password-reset-request", { email })
      .then((response) => {
        setLoading(false);
        alert(response.data.message);
      })
      .catch((error) => {
        setLoading(false);
        setErrorMessage(
          error.response?.data?.message || "Error sending reset link"
        );
      });
  };

  return (
    <div className="card auth-card">
      {!resetMode ? (
        // Login form
        <form onSubmit={handleLoginSubmit}>
          <h2>Login</h2>
          {errorMessage && <p className="error-message">{errorMessage}</p>}{" "}
          {/* Show error messages */}
          <label>Username: </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label>Password: </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Logging In..." : "Login"}
          </button>
          <p>
            Forgot your password?{" "}
            <Link to="#" onClick={() => setResetMode(true)}>
              Reset Password
            </Link>
          </p>
        </form>
      ) : (
        // Password Reset Form
        <form onSubmit={handlePasswordResetSubmit}>
          <h2>Reset Password</h2>
          {errorMessage && <p className="error-message">{errorMessage}</p>}{" "}
          {/* Show error messages */}
          <label>Email: </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send Reset Link"}
          </button>
          <p>
            Remember your password?{" "}
            <Link to="#" onClick={() => setResetMode(false)}>
              Login here
            </Link>
          </p>
        </form>
      )}
    </div>
  );
}

export default Auth;
