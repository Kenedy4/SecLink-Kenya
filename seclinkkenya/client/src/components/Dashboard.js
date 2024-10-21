import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate(); // For redirecting the user if session is invalid

  useEffect(() => {
    const token = localStorage.getItem('token');  // Get token from localStorage
    if (!token) {
      // If no token exists, redirect the user to the login page
      navigate('/login');
      return;
    }

    // Check session using the token
    axios.get('http://localhost:5555/check-session', {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then((response) => {
      setUserData(response.data);  // Set the user data if the session is valid
    })
    .catch((error) => {
      console.error(error.response?.data?.error || 'Error checking session');
      // If there's an error (e.g., session expired), redirect to login
      navigate('/login');
    });
  }, [navigate]);

  return (
    <div>
      {userData ? (
        <div>
          <h2>Welcome, {userData.username}</h2>
          <p>Role: {userData.role}</p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default Dashboard;
