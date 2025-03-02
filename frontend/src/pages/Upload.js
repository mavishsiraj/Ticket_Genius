import { useState } from "react";
import { processDocument } from "../api/api";
import { Container, Button, Form, Card } from "react-bootstrap";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    const result = await processDocument(file);
    setResponse(result);
  };

  return (
    <Container className="mt-4">
      <h2 className="text-center">AI-Powered Document Analysis</h2>
      <Form.Group controlId="formFile">
        <Form.Control type="file" onChange={(e) => setFile(e.target.files[0])} />
      </Form.Group>
      <Button className="mt-2" variant="primary" onClick={handleUpload}>
        Upload
      </Button>

      {response && (
        <Card className="mt-4 p-3">
          <h4>Extracted Text:</h4>
          <p>{response.extracted_text}</p>
          <h4>Summary:</h4>
          <p>{response.summary}</p>
        </Card>
      )}
    </Container>
  );
};

export default Upload;
