# Ticket Genius - AI-Powered IT Support Ticketing System

## Overview
Ticket Genius is an AI-driven intelligent process automation system designed to streamline IT support ticket management. It leverages Natural Language Processing (NLP), AI classification, sentiment analysis, and machine learning to automate ticket classification, routing, resolution suggestions, document processing, and real-time insights.

## Features
- **AI-Powered Ticket Lifecycle Automation**
  - Dynamic classification of tickets without hardcoded rules.
  - Sentiment analysis for urgency detection.
  - Automatic assignment to the right team and engineer.
  
- **Automated Ticket Summarization & Resolution Suggestions**
  - AI generates concise summaries of ticket descriptions.
  - Provides AI-driven resolution suggestions based on historical data.

- **AI-Driven Document Processing**
  - OCR-based extraction of key information from uploaded documents (e.g., invoices, error logs, warranty cards).

- **Chatbot Support for Engineers**
  - Engineers can chat with AI to retrieve ticket details, summaries, and resolution steps.
  - Provides real-time troubleshooting guidance.

## Tech Stack
- **Frontend:** React.js, Bootstrap
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL/MySQL
- **AI Models:** Gemini AI (Google), OpenAI GPT, OCR for document extraction
- **Authentication:** JWT-based authentication
- **Deployment:** Docker, AWS/GCP

## Installation & Setup
### Prerequisites
- Python 3.8+
- Node.js & npm
- PostgreSQL/MySQL database
- OpenAI API key (or Gemini API key)

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/mavishsiraj/Ticket_Genius.git
cd Ticket_Genius/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start the React app
npm start
```

## API Endpoints
### User Authentication
- **`POST /login`** - Authenticates user and provides JWT token.

### Ticket Management
- **`POST /tickets/`** - Create a new ticket.
- **`GET /tickets/`** - Retrieve all tickets.
- **`GET /tickets/{ticket_id}/`** - Fetch ticket details.
- **`PUT /tickets/{ticket_id}/`** - Update ticket status or details.
- **`DELETE /tickets/{ticket_id}/`** - Delete a ticket.

### AI Features
- **`POST /process_document/`** - Extracts key details from uploaded files.
- **`POST /chatbot/`** - AI-powered chatbot for engineers.

## Expected Outcomes
- **Faster Ticket Resolutions:** AI-driven classification and routing.
- **Reduced Workload:** Automated resolution suggestions for engineers.
- **Improved User Experience:** Quick issue handling and better insights for IT managers.

## Contributors
- **Taiba Siraj** - Lead Developer
- **OpenAI/Gemini AI** - AI Model Integration
- **Community Contributions Welcome!**

## License
This project is licensed under the MIT License. Feel free to contribute!

## Contact
For any queries, reach out via [LinkedIn](https://www.linkedin.com/in/taiba-siraj/) or email at **mavishsiraj1@gmail.com**.

