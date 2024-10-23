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
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    setIsRole(role);
    if (!token) {
      navigate("/login");
      return;
    } else {
      setIsAuthenticated(true);
    }
  }, [navigate]);

  const handleLogout = () => {
    const token = localStorage.getItem("token");

    // Send a request to the backend to log out
    axios
      .post(
        "http://localhost:5555/logout",
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`, // Include the token in the Authorization header
          },
        }
      )
      .then((response) => {
        console.log(response.data.message);
        // Clear token and redirect to login
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        navigate("/login");
      })
      .catch((error) => {
        console.error("Logout failed", error);
      });
  };

  if (!isAuthenticated) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {/* <h1>Dashboard</h1> */}
      {/* Render dashboard content */}
      {isRole === "Parent" ? <ParentDashboard /> : <TeacherDashboard />}

      {/* Logout button */}
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;
