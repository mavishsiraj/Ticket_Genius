import React, { useEffect, useState } from "react";
import { fetchTickets } from "../api/api"; 
import { Table, Container } from "react-bootstrap";

const Tickets = () => {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    const getTickets = async () => {
      try {
        const data = await fetchTickets();
        setTickets(data);
      } catch (error) {
        console.error("Error fetching tickets:", error);
      }
    };
    getTickets();
  }, []);

  return (
    <Container className="mt-4">
      <h2 className="text-center">Tech Support Requests</h2>
      <Table striped bordered hover responsive>
        <thead className="bg-dark text-white text-center">
          <tr>
            <th>ID</th>
            <th>Subject</th>
            <th>Description</th>
            <th>Summary</th>
            <th>Priority</th>
            <th>Assigned Engineer</th>
            <th>Team</th>
            <th>Creation Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>{ticket.id}</td>
              <td>{ticket.subject}</td>
              <td>{ticket.description}</td>
              <td>{ticket.summary}</td>
              <td>{ticket.priority}</td>
              <td>{ticket.assigned_engineer_name || "Unassigned"}</td>
              <td>{ticket.assigned_team_name || "Unassigned"}</td>
              <td>{new Date(ticket.created_at).toLocaleString()}</td>
              <td>{ticket.status}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default Tickets;
