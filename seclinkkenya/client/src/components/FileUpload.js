import React, { useState } from "react";
import axios from "axios";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);

    const token = localStorage.getItem("token");

    axios
      .post("https://seclink-server.onrender.com/upload", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        alert(response.data.message);
      })
      .catch((error) => {
        alert(error.response.data.error || "Error uploading file");
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Upload Learning Material</h2>
      <label>Title: </label>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <label>File: </label>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        required
      />

      <button type="submit">Upload</button>
    </form>
  );
}

export default FileUpload;
