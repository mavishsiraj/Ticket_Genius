import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="container text-center mt-5">
      <h1 className="display-4 fw-bold text-primary"> Welcome to Ticket Genius</h1>
      <p className="lead text-muted">
        AI-powered IT support that automates ticket management, reduces response times, and enhances troubleshooting with intelligent assistance.
      </p>

      <div className="row mt-5">
        <div className="col-md-4">
          <h3> AI-Powered Ticketing</h3>
          <p>Classify and prioritize issues instantly with AI.</p>
        </div>
        <div className="col-md-4">
          <h3> AI Chatbot Support</h3>
          <p>Instant troubleshooting help from our AI assistant.</p>
        </div>
        <div className="col-md-4">
          <h3> Smart Document Processing</h3>
          <p>Analyze logs, invoices, and reports using AI.</p>
        </div>
      </div>

      <div className="mt-4">
        <Link to="/tickets" className="btn btn-primary btn-lg mx-2"> View Tickets</Link>
        <Link to="/chatbot" className="btn btn-success btn-lg mx-2"> Chat with AI</Link>
        <Link to="/new-ticket" className="btn btn-warning btn-lg mx-2"> Create a Ticket</Link>
      </div>
    </div>
  );
};

export default Home;
