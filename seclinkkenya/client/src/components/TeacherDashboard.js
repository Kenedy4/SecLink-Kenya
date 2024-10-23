import React, { useEffect, useState } from "react";
import axios from "axios";

const TeacherDashboard = () => {
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [materialTitle, setMaterialTitle] = useState("");

  // Fetch all students or by class ID
  const getStudents = async (classId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        `https://seclink-server.onrender.com/students`,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { class_id: classId || "" }
        }
      );
      setStudents(response.data);
    } catch (error) {
      console.error("Error fetching students:", error.response?.data?.message || error);
    }
  };

  // Fetch all classes
  const getClasses = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get("https://seclink-server.onrender.com/classes", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setClasses(response.data);
    } catch (error) {
      console.error("Error fetching classes:", error.response?.data?.message || error);
    }
  };

  // Fetch learning materials
  const getLearningMaterials = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        "https://seclink-server.onrender.com/learning-material",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setLearningMaterials(response.data);
    } catch (error) {
      console.error("Error fetching learning materials:", error.response?.data?.message || error);
    }
  };

  // Fetch notifications
  const getNotifications = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get("https://seclink-server.onrender.com/notifications", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications(response.data);
    } catch (error) {
      console.error("Error fetching notifications:", error.response?.data?.message || error);
    }
  };

  // Upload learning material
  const uploadLearningMaterial = async (event) => {
    event.preventDefault();
    if (!selectedFile || !materialTitle) {
      alert("Please fill in all fields.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("title", materialTitle);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "https://seclink-server.onrender.com/learning-material",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("Learning material uploaded successfully", response.data);
      getLearningMaterials(); // Refresh learning materials
    } catch (error) {
      console.error("Error uploading learning material:", error.response?.data?.message || error);
    }
  };

  // Handle file input change
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
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

        {/* Upload new learning material */}
        <h3>Upload New Learning Material</h3>
        <form onSubmit={uploadLearningMaterial}>
          <label>
            Title:
            <input
              type="text"
              value={materialTitle}
              onChange={(e) => setMaterialTitle(e.target.value)}
              required
            />
          </label>
          <label>
            Select File:
            <input type="file" onChange={handleFileChange} required />
          </label>
          <button type="submit">Upload</button>
        </form>
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
      </div>
    </div>
  );
};

export default TeacherDashboard;
