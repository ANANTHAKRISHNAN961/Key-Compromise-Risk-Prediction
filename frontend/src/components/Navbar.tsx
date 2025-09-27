import React from 'react';
import { Link } from 'react-router-dom'; // <--- IMPORT Link
import './Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        🛡️ Project Chimera
      </div>
      <ul className="navbar-links">
        {/* Replace <a> tags with <Link> */}
        <li><Link to="/">Home</Link></li>
        <li><Link to="/inventory">Inventory</Link></li>
        <li><Link to="/access-logs">Access Logs</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;