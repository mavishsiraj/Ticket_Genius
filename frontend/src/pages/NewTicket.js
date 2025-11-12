import { useState } from "react";
import { createTicket } from "../api/api";

const NewTicket = () => {
  const [userId, setUserId] = useState("");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const token = localStorage.getItem("access_token"); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResponse(null);

    const ticketData = {
      user_id: parseInt(userId), 
      subject,
      description,
    };

    const result = await createTicket(ticketData, token);
    if (result.error) {
      setError(result.error);
    } else {
      setResponse(result);
    }
  };

  return (
    <div className="container mt-5">
      <h2>Create New Ticket</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">User ID:</label>
          <input
            type="number"
            className="form-control"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Subject:</label>
          <input
            type="text"
            className="form-control"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Description:</label>
          <textarea
            className="form-control"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Submit Ticket
        </button>
      </form>

      {response && (
        <div className="alert alert-success mt-4">
          <h4>Ticket Created Successfully!</h4>
          <p><strong>ID:</strong> {response.id}</p>
          <p><strong>Summary:</strong> {response.summary}</p>
          <p><strong>Suggested Resolution:</strong> {response.suggested_resolution}</p>
          <p><strong>Status:</strong> {response.status}</p>
        </div>
      )}

      {error && <div className="alert alert-danger mt-4">Error: {error}</div>}
    </div>
  );
};

export default NewTicket;
