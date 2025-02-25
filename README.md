Ticket Genius - AI-Powered IT Support System
 Ticket Genius is an AI-powered IT support system that automates ticket classification, summarization, resolution suggestions, and chatbot interactions for engineers.

 Features
  AI Ticket Classification – Classifies tickets dynamically based on descriptions using NLP.
  Summarization – Automatically summarizes ticket descriptions for quick resolution.
  AI Chatbot – An interactive chatbot to assist engineers in resolving tickets.
  OCR & Document Processing – Extracts text from uploaded documents for AI analysis.
  Intelligent Ticket Routing – Assigns tickets to appropriate teams based on AI analysis.
  Real-Time Insights – Engineers can view open tickets, trends, and automated resolutions.

 Technologies Used

Backend (FastAPI + AI Processing)
FastAPI – High-performance API framework.
SQLAlchemy – Database ORM.
MySQL – Database for storing tickets and users.
Spacy – NLP library for text processing.
Google Gemini AI – Used for AI-powered classification & chatbot interactions.
Pydantic – Data validation.
OpenAI API (optional) – For alternative chatbot capabilities.
Frontend (React + Bootstrap)
React.js – Frontend framework.
React Bootstrap – UI components for a professional design.
Fetch API – For making API calls.  

Setup Instructions

Backend (FastAPI) Setup
Clone the repository
git clone https://github.com/yourusername/ticket-genius.git
cd ticket-genius/backend
Create a virtual environment & install dependencies
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
Set up environment variables
export OPENAI_API_KEY="your_openai_key"
export DATABASE_URL="mysql+pymysql://user:password@localhost/ticket_db"
Run the FastAPI server
uvicorn main:app --reload
Access API docs:
  Open http://127.0.0.1:8000/docs for interactive Swagger UI.

Frontend (React) Setup
Go to frontend directory & install dependencies
cd ../frontend
npm install
Run the frontend app
npm start
Access the app:
Open http://localhost:3000 in your browser.

API Endpoints
Authentication
POST /login – Authenticate user and get a JWT token.
Ticket Management
POST /tickets/ – Create a new ticket.
GET /tickets/ – Get all tickets.
GET /tickets/{ticket_id} – Get a specific ticket by ID.
PUT /tickets/{ticket_id} – Update ticket details.
DELETE /tickets/{ticket_id} – Delete a ticket.
Chatbot
POST /chatbot/ – AI-powered IT chatbot interaction.
Document Processing
POST /process_document/ – Upload and process documents (OCR & AI analysis).

Project Structure

ticket-genius/
│── backend/
│   ├── main.py              # FastAPI backend
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   ├── database.py          # Database setup
│   ├── openai_utils.py      # AI-related functions
│── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Main pages
│   │   ├── api/             # API calls
│   │   ├── App.js           # Main app file
│   │   ├── index.js         # Entry point
│── public/
│── README.md                # Project documentation
│── requirements.txt         # Python dependencies
│── package.json             # Frontend dependencies

