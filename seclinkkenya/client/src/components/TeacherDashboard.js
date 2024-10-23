import React, { useEffect, useState } from 'react';
// import './TeacherDashboard.css'; // Make sure this file exists in the same folder

const TeacherDashboard = () => {
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // Fetch all students or by class ID
  const getStudents = async (classId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5555/students?class_id=${classId || ''}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setStudents(data);
      } else {
        console.error('Error fetching students:', data.message);
      }
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  // Fetch all classes
  const getClasses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5555/classes', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setClasses(data);
      } else {
        console.error('Error fetching classes:', data.message);
      }
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  // Fetch learning materials
  const getLearningMaterials = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5555/learning-material', {
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

  // Fetch notifications
  const getNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5555/notifications', {
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

  // Upload learning material
  const uploadLearningMaterial = async (materialData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5555/learning-material', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(materialData)
      });
      const data = await response.json();
      if (response.ok) {
        console.log('Learning material uploaded successfully', data);
        getLearningMaterials(); // Refresh learning materials
      } else {
        console.error('Error uploading learning material:', data.message);
      }
    } catch (error) {
      console.error('Error uploading learning material:', error);
    }
  };

  // Add notification to parents
  const addNotification = async (notificationData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5555/notifications', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(notificationData)
      });
      const data = await response.json();
      if (response.ok) {
        console.log('Notification added successfully', data);
        getNotifications(); // Refresh notifications
      } else {
        console.error('Error adding notification:', data.message);
      }
    } catch (error) {
      console.error('Error adding notification:', error);
    }
  };

  useEffect(() => {
    getStudents();
    getClasses();
    getLearningMaterials();
    getNotifications();
  }, []);

  return (
    <div>
      <h1>Teacher Dashboard</h1>

      <div id="students">
        <h2>Students</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Class</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.id}</td>
                <td>{student.name}</td>
                <td>{student.class}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div id="classes">
        <h2>Classes</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Teacher</th>
            </tr>
          </thead>
          <tbody>
            {classes.map((classItem) => (
              <tr key={classItem.id}>
                <td>{classItem.id}</td>
                <td>{classItem.name}</td>
                <td>{classItem.teacher}</td>
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
              <th>ID</th>
              <th>Title</th>
              <th>File Path</th>
            </tr>
          </thead>
          <tbody>
            {learningMaterials.map((material) => (
              <tr key={material.id}>
                <td>{material.id}</td>
                <td>{material.title}</td>
                <td>{material.file_path}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Button to upload learning materials */}
        <button onClick={() => uploadLearningMaterial({ title: 'New Material', file_path: '/path/to/file' })}>
          Upload Learning Material
        </button>
      </div>

      <div id="notifications">
        <h2>Notifications</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Message</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {notifications.map((notification) => (
              <tr key={notification.id}>
                <td>{notification.id}</td>
                <td>{notification.message}</td>
                <td>{notification.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Button to send notifications */}
        <button onClick={() => addNotification({ message: "New notification for parents", parent_id: 1 })}>
          Send Notification
        </button>
      </div>
    </div>
  );
};

export default TeacherDashboard;
