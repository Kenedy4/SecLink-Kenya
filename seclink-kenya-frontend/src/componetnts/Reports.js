import React, { useState } from 'react';
import axios from 'axios';

const Reports = () => {
  const [report, setReport] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/reports', { report });
      alert('Report sent successfully!');
    } catch (error) {
      console.error('Error sending report', error);
    }
  };

  return (
    <div className="reports-container">
      <h2>Submit Student Report</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={report}
          onChange={(e) => setReport(e.target.value)}
          placeholder="Write your report..."
        />
        <button type="submit">Send Report</button>
      </form>
    </div>
  );
};

export default Reports;
