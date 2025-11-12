const API_URL = "http://localhost:8000";
const BASE_URL = "http://localhost:8000";

export const fetchTickets = async () => {
  const response = await fetch(`${API_URL}/tickets/`);
  return response.json();
};

export const processDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/process_document/`, {
    method: "POST",
    body: formData,
  });

  return response.json();
};

// Chatbot API
export const chatWithBot = async (userId, messages = []) => {
  console.log("Messages Sent to Bot:", messages);

  try {
    const response = await fetch("http://127.0.0.1:8000/chatbot/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        messages
      }),
    });

    console.log("Response Status:", response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error Response:", errorData);
      throw new Error(`Error: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log("Bot Response:", data);
    return data;

  } catch (error) {
    console.error("Fetch Error:", error.message);
    return { error: error.message };
  }
};


export const createTicket = async (ticketData, token) => {
  console.log("Sending ticket data:", JSON.stringify(ticketData));

  const response = await fetch(`${BASE_URL}/tickets/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(ticketData),
  });

  console.log("Response Status:", response.status);

  if (!response.ok) {
    const errorData = await response.json();
    console.error("Error Response:", errorData);
    throw new Error(`Error: ${errorData.detail || response.statusText}`);
  }

  const responseData = await response.json();
  console.log("Ticket Created:", responseData);
  return responseData;
};



