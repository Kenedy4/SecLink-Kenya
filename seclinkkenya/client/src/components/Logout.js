import React from "react";
import { useNavigate } from "react-router-dom";

function Logout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Remove the JWT token from localStorage
    localStorage.removeItem("token");

    // Optionally, you can call the backend logout endpoint if you are blacklisting tokens
    fetch("https://seclink-server.onrender.com/logout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((response) => {
        if (response.ok) {
          console.log("Logged out successfully");
        }
      })
      .catch((error) => console.error("Error logging out:", error));

    // Redirect the user to the login page
    navigate("/login");
  };

  return <button onClick={handleLogout}>Logout</button>;
}

export default Logout;
