import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import AccessLogsPage from './pages/AccessLogsPage';
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
          <Route path="/access-logs" element={<AccessLogsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;