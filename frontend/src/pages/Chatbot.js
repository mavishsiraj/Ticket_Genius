import { useState } from "react";
import { chatWithBot } from "../api/api";
import { Container, Form, Button, Card } from "react-bootstrap";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const userId = 5; 

  const handleChat = async () => {
    const result = await chatWithBot(query, userId, chatHistory);

    if (result.response) {
      setChatHistory([...chatHistory, query]); 
      setResponse(result.response);
    } else {
      setResponse("Something went wrong.");
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

      {response && (
        <Card className="mt-4 p-3">
          <h5>Bot Response:</h5>
          <p>{response}</p>
        </Card>
      )}
    </Container>
  );
};

export default Chatbot;
