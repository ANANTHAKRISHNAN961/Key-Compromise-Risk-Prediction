import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import InventoryPage from './pages/InventoryPage';

function App() {
  return (
    <Router>
      <div>
        <Navbar />
        <Routes>
          <Route index path="/" element={<HomePage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          {/* Add a placeholder for the Access Logs page */}
          <Route path="/access-logs" element={
            <div className="container">
              <h1>Access Logs (Coming Soon)</h1>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;