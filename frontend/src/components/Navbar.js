import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">Ticket Genius</Link>
        <div className="collapse navbar-collapse">
          <ul className="navbar-nav">
            <li className="nav-item"><Link className="nav-link" to="/tickets">Tickets</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/upload">Upload</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/chatbot">Chatbot</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/new-ticket">Create Ticket</Link></li> {/* New Link */}
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
