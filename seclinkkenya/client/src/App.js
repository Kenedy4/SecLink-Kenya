import './App.css';
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Signup from './components/Signup';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import PasswordReset from './components/PasswordReset';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<FileUpload />} />
          <Route path="/password-reset" element={<PasswordReset />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
