import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";

const TeacherDashboard = () => {
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [learningMaterials, setLearningMaterials] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [materialTitle, setMaterialTitle] = useState("");
  const [notificationMessage, setNotificationMessage] = useState("");
  const [sendToAll, setSendToAll] = useState(false);
  const [selectedClassId, setSelectedClassId] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentDetails, setStudentDetails] = useState({});
  const [classDetails, setClassDetails] = useState({});
  const [selectedNotification, setSelectedNotification] = useState(null); // For updating notification
  const token = localStorage.getItem("token");

  // Fetch all students or by class ID
  const getStudents = useCallback(async () => {
    try {
      const response = await axios.get("https://seclink-server.onrender.com/students", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStudents(response.data);
    } catch (error) {
      console.error("Error fetching students:", error);
    }
  }, [token]);

  // Fetch all classes
  const getClasses = useCallback(async () => {
    try {
      const response = await axios.get("https://seclink-server.onrender.com/classes", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setClasses(response.data);
    } catch (error) {
      console.error("Error fetching classes:", error);
    }
  }, [token]);

  // Fetch learning materials
  const getLearningMaterials = useCallback(async () => {
    try {
      const response = await axios.get("https://seclink-server.onrender.com/learning-material", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLearningMaterials(response.data);
    } catch (error) {
      console.error("Error fetching learning materials:", error);
    }
  }, [token]);

  // Fetch notifications
  const getNotifications = useCallback(async () => {
    try {
      const response = await axios.get("https://seclink-server.onrender.com/notifications", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications(response.data);
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  }, [token]);

  // Add New Student
  const addStudent = async () => {
    try {
      await axios.post("https://seclink-server.onrender.com/students", studentDetails, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getStudents(); // Refresh the student list
      setStudentDetails({}); // Clear student details
    } catch (error) {
      console.error("Error adding student:", error);
    }
  };

  // Update Student Details
  const updateStudent = async () => {
    if (!selectedStudent) return;

    try {
      await axios.put(`https://seclink-server.onrender.com/students/${selectedStudent.id}`, studentDetails, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getStudents(); // Refresh the student list
      setSelectedStudent(null); // Reset selection after update
      setStudentDetails({}); // Clear student details
    } catch (error) {
      console.error("Error updating student:", error);
    }
  };

  // Delete Student
  const deleteStudent = async (studentId) => {
    try {
      await axios.delete(`https://seclink-server.onrender.com/students/${studentId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getStudents(); // Refresh the student list
    } catch (error) {
      console.error("Error deleting student:", error);
    }
  };

  // Add New Class
  const addClass = async () => {
    try {
      await axios.post("https://seclink-server.onrender.com/classes", classDetails, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getClasses(); // Refresh the class list
      setClassDetails({}); // Clear class details
    } catch (error) {
      console.error("Error adding class:", error);
    }
  };

  // Update Class
  const updateClass = async (classId) => {
    try {
      await axios.put(`https://seclink-server.onrender.com/classes/${classId}`, classDetails, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getClasses(); // Refresh the class list
      setClassDetails({}); // Clear class details
    } catch (error) {
      console.error("Error updating class:", error);
    }
  };

  // Delete Class
  const deleteClass = async (classId) => {
    try {
      await axios.delete(`https://seclink-server.onrender.com/classes/${classId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getClasses(); // Refresh the class list
    } catch (error) {
      console.error("Error deleting class:", error);
    }
  };

  // Upload Learning Material
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
      await axios.post("https://seclink-server.onrender.com/learning-material", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });
      getLearningMaterials(); // Refresh learning materials
      setSelectedFile(null); // Clear selected file
      setMaterialTitle(""); // Clear title
    } catch (error) {
      console.error("Error uploading learning material:", error);
    }
  };

  // Delete Learning Material
  const deleteLearningMaterial = async (materialId) => {
    try {
      await axios.delete(`https://seclink-server.onrender.com/learning-material/${materialId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getLearningMaterials(); // Refresh learning materials
    } catch (error) {
      console.error("Error deleting learning material:", error);
    }
  };

  // Send Notification
  const sendNotification = async () => {
    const notificationData = {
      message: notificationMessage,
      send_to_all: sendToAll,
      class_id: sendToAll ? selectedClassId : null,
    };

    try {
      await axios.post("https://seclink-server.onrender.com/notifications", notificationData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getNotifications(); // Refresh notifications
      setNotificationMessage(""); // Clear message
    } catch (error) {
      console.error("Error sending notification:", error);
    }
  };

  // Update Notification
  const updateNotification = async () => {
    if (!selectedNotification) return;

    const updatedData = {
      message: notificationMessage, // Use the message input
    };

    try {
      await axios.put(`https://seclink-server.onrender.com/notifications/${selectedNotification.id}`, updatedData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      getNotifications(); // Refresh notifications
      setSelectedNotification(null); // Reset selection after update
      setNotificationMessage(""); // Clear message
    } catch (error) {
      console.error("Error updating notification:", error);
    }
  };

  useEffect(() => {
    getStudents();
    getClasses();
    getLearningMaterials();
    getNotifications();
  }, [token, getStudents, getClasses, getLearningMaterials, getNotifications]);

  return (
    <div>
      <h1>Teacher Dashboard</h1>

      {/* Students Section */}
      <div id="students">
        <h2>Students</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Class</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>{student.id}</td>
                  <td>{student.name}</td>
                  <td>{student.class}</td>
                  <td>
                    <button onClick={() => {
                      setSelectedStudent(student);
                      setStudentDetails({
                        name: student.name,
                        dob: student.dob,
                        overall_grade: student.overall_grade,
                        class_id: student.class_id,
                        teacher_id: student.teacher_id,
                        parent_id: student.parent_id
                      });
                    }}>
                      Update
                    </button>
                    <button onClick={() => deleteStudent(student.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <h3>Add New Student</h3>
        <form onSubmit={addStudent}>
          <label>
            Name:
            <input type="text" value={studentDetails.name || ''} onChange={(e) => setStudentDetails({ ...studentDetails, name: e.target.value })} required />
          </label>
          <label>
            DOB:
            <input type="date" value={studentDetails.dob || ''} onChange={(e) => setStudentDetails({ ...studentDetails, dob: e.target.value })} required />
          </label>
          <label>
            Overall Grade:
            <input type="text" value={studentDetails.overall_grade || ''} onChange={(e) => setStudentDetails({ ...studentDetails, overall_grade: e.target.value })} required />
          </label>
          <label>
            Class ID:
            <input type="text" value={studentDetails.class_id || ''} onChange={(e) => setStudentDetails({ ...studentDetails, class_id: e.target.value })} required />
          </label>
          <label>
            Teacher ID:
            <input type="text" value={studentDetails.teacher_id || ''} onChange={(e) => setStudentDetails({ ...studentDetails, teacher_id: e.target.value })} required />
          </label>
          <label>
            Parent ID:
            <input type="text" value={studentDetails.parent_id || ''} onChange={(e) => setStudentDetails({ ...studentDetails, parent_id: e.target.value })} required />
          </label>
          <button type="submit">Add Student</button>
        </form>

        {/* Update Student Form */}
        {selectedStudent && (
          <div>
            <h3>Update Student Details</h3>
            <form onSubmit={updateStudent}>
              <label>
                Name:
                <input type="text" value={studentDetails.name} onChange={(e) => setStudentDetails({ ...studentDetails, name: e.target.value })} required />
              </label>
              <label>
                DOB:
                <input type="date" value={studentDetails.dob} onChange={(e) => setStudentDetails({ ...studentDetails, dob: e.target.value })} required />
              </label>
              <label>
                Overall Grade:
                <input type="text" value={studentDetails.overall_grade} onChange={(e) => setStudentDetails({ ...studentDetails, overall_grade: e.target.value })} required />
              </label>
              <label>
                Class ID:
                <input type="text" value={studentDetails.class_id} onChange={(e) => setStudentDetails({ ...studentDetails, class_id: e.target.value })} required />
              </label>
              <label>
                Teacher ID:
                <input type="text" value={studentDetails.teacher_id} onChange={(e) => setStudentDetails({ ...studentDetails, teacher_id: e.target.value })} required />
              </label>
              <label>
                Parent ID:
                <input type="text" value={studentDetails.parent_id} onChange={(e) => setStudentDetails({ ...studentDetails, parent_id: e.target.value })} required />
              </label>
              <button type="submit">Update</button>
              <button type="button" onClick={() => setSelectedStudent(null)}>Cancel</button>
            </form>
          </div>
        )}
      </div>

      {/* Classes Section */}
      <div id="classes">
        <h2>Classes</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Teacher</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {classes.map((classItem) => (
                <tr key={classItem.id}>
                  <td>{classItem.id}</td>
                  <td>{classItem.name}</td>
                  <td>{classItem.teacher}</td>
                  <td>
                    <button onClick={() => {
                      setClassDetails({
                        id: classItem.id,
                        name: classItem.name,
                        teacher_id: classItem.teacher_id
                      });
                    }}>
                      Update
                    </button>
                    <button onClick={() => deleteClass(classItem.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <h3>Add New Class</h3>
        <form onSubmit={addClass}>
          <label>
            Class Name:
            <input type="text" value={classDetails.class_name || ''} onChange={(e) => setClassDetails({ ...classDetails, class_name: e.target.value })} required />
          </label>
          <label>
            Teacher ID:
            <input type="text" value={classDetails.teacher_id || ''} onChange={(e) => setClassDetails({ ...classDetails, teacher_id: e.target.value })} required />
          </label>
          <button type="submit">Add Class</button>
        </form>

        {/* Update Class Form */}
        {classDetails.id && (
          <div>
            <h3>Update Class Details</h3>
            <form onSubmit={() => updateClass(classDetails.id)}>
              <label>
                Class Name:
                <input type="text" value={classDetails.class_name} onChange={(e) => setClassDetails({ ...classDetails, class_name: e.target.value })} required />
              </label>
              <label>
                Teacher ID:
                <input type="text" value={classDetails.teacher_id} onChange={(e) => setClassDetails({ ...classDetails, teacher_id: e.target.value })} required />
              </label>
              <button type="submit">Update</button>
              <button type="button" onClick={() => setClassDetails({})}>Cancel</button>
            </form>
          </div>
        )}
      </div>

      {/* Learning Materials Section */}
      <div id="learningMaterials">
        <h2>Learning Materials</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {learningMaterials.map((material) => (
                <tr key={material.id}>
                  <td>{material.id}</td>
                  <td>{material.title}</td>
                  <td>
                    <button onClick={() => deleteLearningMaterial(material.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <h3>Upload New Learning Material</h3>
        <form onSubmit={uploadLearningMaterial}>
          <label>
            Title:
            <input type="text" value={materialTitle} onChange={(e) => setMaterialTitle(e.target.value)} required />
          </label>
          <label>
            Select File:
            <input type="file" onChange={(e) => setSelectedFile(e.target.files[0])} required />
          </label>
          <button type="submit">Upload</button>
        </form>
      </div>

      {/* Notifications Section */}
      <div id="notifications">
        <h2>Notifications</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Message</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {notifications.map((notification) => (
                <tr key={notification.id}>
                  <td>{notification.id}</td>
                  <td>{notification.message}</td>
                  <td>{notification.date}</td>
                  <td>
                    <button onClick={() => {
                      setSelectedNotification(notification); // Set the selected notification for update
                      setNotificationMessage(notification.message); // Populate the message
                    }}>
                      Update
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <h3>Send Notification</h3>
        <input
          type="text"
          value={notificationMessage}
          onChange={(e) => setNotificationMessage(e.target.value)}
          placeholder="Enter notification message"
        />
        <label>
          <input
            type="checkbox"
            checked={sendToAll}
            onChange={() => setSendToAll(!sendToAll)}
          />
          Send to all parents in the class
        </label>
        {sendToAll && (
          <select onChange={(e) => setSelectedClassId(e.target.value)} required>
            <option value="">Select Class</option>
            {classes.map((classItem) => (
              <option key={classItem.id} value={classItem.id}>{classItem.name}</option>
            ))}
          </select>
        )}
        <button onClick={sendNotification}>Send Notification</button>

        {/* Update Notification Form */}
        {selectedNotification && (
          <div>
            <h3>Update Notification</h3>
            <form onSubmit={updateNotification}>
              <label>
                Message:
                <input
                  type="text"
                  value={notificationMessage}
                  onChange={(e) => setNotificationMessage(e.target.value)}
                  required
                />
              </label>
              <button type="submit">Update</button>
              <button type="button" onClick={() => setSelectedNotification(null)}>Cancel</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;
