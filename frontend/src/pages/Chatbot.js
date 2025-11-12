import { useState } from "react";
import { chatWithBot } from "../api/api";
import { Container, Form, Button, Card } from "react-bootstrap";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const userId = 5;

  const handleChat = async () => {
    if (!query.trim()) return;
    const updatedHistory = [
      ...chatHistory,
      { role: "user", content: query }
    ];

    const result = await chatWithBot(userId, updatedHistory);

    if (result.response) {
      setChatHistory([
        ...updatedHistory,
        { role: "assistant", content: result.response }
      ]);
      setQuery(""); // Clear input
    }
  };

  return (
    <Container className="mt-4">
      <h2 className="text-center">AI Chatbot</h2>
      <Form.Control
        type="text"
        placeholder="Ask something..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <Button className="mt-2" variant="success" onClick={handleChat}>
        Send
      </Button>

      {chatHistory.length > 0 && (
        <Card className="mt-4 p-3">
          <h5>Conversation:</h5>
          {chatHistory.map((msg, idx) => (
            <div key={idx} style={{ textAlign: msg.role === "user" ? "right" : "left" }}>
              <b>{msg.role === "user" ? "You" : "Bot"}:</b> {msg.content}
            </div>
          ))}
        </Card>
      )}
    </Container>
  );
};

export default Chatbot;
