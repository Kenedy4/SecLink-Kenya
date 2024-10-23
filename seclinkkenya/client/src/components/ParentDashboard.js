// src/components/Dashboard.js

import React, { useEffect, useState } from 'react';

const Dashboard = () => {
  const [studentDetails, setStudentDetails] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);

  // Fetch Student Details
  const getStudentDetails = async (studentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/students/${studentId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setStudentDetails(data);
      } else {
        console.error('Error fetching student details:', data.message);
      }
    } catch (error) {
      console.error('Error fetching student details:', error);
    }
  };

  // Fetch Notifications
  const getNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/notifications', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setNotifications(data);
      } else {
        console.error('Error fetching notifications:', data.message);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  // Fetch Learning Materials
  const downloadLearningMaterials = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/learning-material', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setLearningMaterials(data);
      } else {
        console.error('Error fetching learning materials:', data.message);
      }
    } catch (error) {
      console.error('Error fetching learning materials:', error);
    }
  };

  // Fetch the data when the component mounts
  useEffect(() => {
    const exampleStudentId = 1; // Replace with actual logic to get the studentId
    getStudentDetails(exampleStudentId);
    getNotifications();
    downloadLearningMaterials();
  }, []);

  return (
    <div>
      <h1>Parent Dashboard</h1>

      <div id="studentDetails">
        <h2>Student Details</h2>
        <pre>{JSON.stringify(studentDetails, null, 2)}</pre>
      </div>

      <div id="notifications">
        <h2>Notifications</h2>
        <pre>{JSON.stringify(notifications, null, 2)}</pre>
      </div>

      <div id="learningMaterials">
        <h2>Learning Materials</h2>
        <pre>{JSON.stringify(learningMaterials, null, 2)}</pre>
      </div>
    </div>
  );
};

export default Dashboard;
