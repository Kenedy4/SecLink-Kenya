import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LearningMaterials = () => {
  const [materials, setMaterials] = useState([]);

  useEffect(() => {
    const fetchMaterials = async () => {
      const response = await axios.get('/api/learning-materials');
      setMaterials(response.data);
    };
    fetchMaterials();
  }, []);

  return (
    <div className="materials-container">
      <h2>Learning Materials</h2>
      <ul>
        {materials.map((material) => (
          <li key={material.id}>
            <a href={material.url} download>{material.title}</a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LearningMaterials;
