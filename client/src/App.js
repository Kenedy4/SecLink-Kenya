import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from './components/Login';
import ResetPassword from './components/ResetPassword';
import Dashboard from './components/Dashboard';
import LearningMaterials from './components/LearningMaterials';
import Profile from './components/Profile';
import Reports from './components/Reports';
import Notifications from './components/Notifications';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

const App = () => {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <Switch>
          <Route path="/login" component={Login} />
          <Route path="/reset-password" component={ResetPassword} />
          <PrivateRoute path="/dashboard" component={Dashboard} />
          <PrivateRoute path="/learning-materials" component={LearningMaterials} />
          <PrivateRoute path="/profile" component={Profile} />
          <PrivateRoute path="/reports" component={Reports} />
          <PrivateRoute path="/notifications" component={Notifications} />
        </Switch>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
