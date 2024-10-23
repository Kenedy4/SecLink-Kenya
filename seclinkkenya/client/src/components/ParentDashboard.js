import React, { useEffect, useState } from 'react';
// import Navbar from './Navbar';

const ParentDashboard = () => {
  const [studentDetails, setStudentDetails] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);

  // Fetch Student Details
  const getStudentDetails = async (studentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`https://seclink-server.onrender.com/students/${studentId}`, {
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
      const response = await fetch('https://seclink-server.onrender.com/notifications', {
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
      const response = await fetch('https://seclink-server.onrender.com/learning-material', {
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
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Class</th>
              <th>Age</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{studentDetails.name}</td>
              <td>{studentDetails.class_name}</td>
              <td>{studentDetails.age}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div id="notifications">
        <h2>Notifications</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {notifications.map((notification, index) => (
              <tr key={index}>
                <td>{notification.date}</td>
                <td>{notification.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div id="learningMaterials">
        <h2>Learning Materials</h2>
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {learningMaterials.map((material, index) => (
              <tr key={index}>
                <td>{material.title}</td>
                <td>
                  <a href={`https://seclink-server.onrender.com/download/${material.file_path}`} download>
                    Download
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ParentDashboard;
