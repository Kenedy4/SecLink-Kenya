import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import ParentDashboard from "./ParentDashboard";
import TeacherDashboard from "./TeacherDashboard";
function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRole, setIsRole] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");  // Retrieve the token from localStorage
    console.log("THIS TOKEN FROM DASHBOARD ", token)
    const role = localStorage.getItem("role");  // Retrieve the token from localStorage
    console.log("THIS TOKEN FROM role ", role)
    setIsRole(role)
    if (!token) {
      navigate("/login");  // Redirect if no token is found
      return;
    } else {
      setIsAuthenticated(true);
    }
    // var component;
    
    // Make the session check request with the token
  //   axios
  //     .get("http://localhost:5555/check-session", {
  //       headers: {
  //         Authorization: `Bearer ${token}`,  // Include the token in the Authorization header
  //       },
  //     })
  //     .then((response) => {
  //       setIsAuthenticated(true);  // User is authenticated
  //     })
  //     .catch((error) => {
  //       console.error("Session check failed", error);
  //       localStorage.removeItem("token");  // Clear the token if the session check fails
  //       navigate("/login");  // Redirect to login
  //     });
  }, [navigate]);

  if (!isAuthenticated) {
    return <div>Loading...</div>;  // Display loading state until authentication is verified
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Render dashboard content */}
      {isRole === 'Parent' ? <ParentDashboard /> :<TeacherDashboard />}
    </div>
  );
}

export default Dashboard;
