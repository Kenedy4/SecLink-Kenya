import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");  // Retrieve the token from localStorage

    if (!token) {
      navigate("/login");  // Redirect if no token is found
      return;
    }

    // Make the session check request with the token
    axios
      .get("http://localhost:5555/check-session", {
        headers: {
          Authorization: `Bearer ${token}`,  // Include the token in the Authorization header
        },
      })
      .then((response) => {
        setIsAuthenticated(true);  // User is authenticated
      })
      .catch((error) => {
        console.error("Session check failed", error);
        localStorage.removeItem("token");  // Clear the token if the session check fails
        navigate("/login");  // Redirect to login
      });
  }, [navigate]);

  if (!isAuthenticated) {
    return <div>Loading...</div>;  // Display loading state until authentication is verified
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Render dashboard content */}
    </div>
  );
}

export default Dashboard;
