import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    axios.get('http://localhost:5555/check-session', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((response) => {
        setUserData(response.data);
      })
      .catch((error) => {
        alert(error.response.data.error || 'Error fetching session data');
      });
  }, []);

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
