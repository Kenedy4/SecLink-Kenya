import React, { useEffect, useState } from "react";
import axios from "axios";

const ParentDashboard = () => {
  const [studentDetails, setStudentDetails] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);

  // Fetch Student Details
  const getStudentDetails = async (studentId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        `https://seclink-kenya.onrender.com/students/${studentId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setStudentDetails(response.data);
    } catch (error) {
      console.error(
        "Error fetching student details:",
        error.response?.data?.message || error.message
      );
    }
  };

  // Fetch Notifications
  const getNotifications = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        "https://seclink-kenya.onrender.com/notifications",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setNotifications(response.data);
    } catch (error) {
      console.error(
        "Error fetching notifications:",
        error.response?.data?.message || error.message
      );
    }
  };

  // Fetch Learning Materials
  const downloadLearningMaterials = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        "https://seclink-kenya.onrender.com/learning-material",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setLearningMaterials(response.data);
    } catch (error) {
      console.error(
        "Error fetching learning materials:",
        error.response?.data?.message || error.message
      );
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
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Class</th>
                <th>Age</th>
                <th>Subject</th>
                <th>Overall Grade</th>
                <th>Parent ID</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{studentDetails.id}</td>
                <td>{studentDetails.name}</td>
                <td>{studentDetails.class_name}</td>
                <td>{studentDetails.age}</td>
                <td>{studentDetails.subject}</td>
                <td>{studentDetails.overall_grade}</td>
                <td>{studentDetails.parent_id}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div id="notifications">
        <h2>Notifications</h2>
        <div className="table-container">
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
      </div>

      <div id="learningMaterials">
        <h2>Learning Materials</h2>
        <div className="table-container">
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
                    <a
                      href={`https://seclink-server.onrender.com/download/${material.file_path}`}
                      download
                    >
                      Download
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ParentDashboard;
