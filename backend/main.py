# Standard library imports
import io
import os
import time
from typing import Dict, List, Any
from typing import Optional
# Third-party imports
from dotenv import load_dotenv
from fastapi import (
    Depends, FastAPI, File, HTTPException, 
    Request, status, UploadFile
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from PIL import Image
from pydantic import BaseModel
import filetype
import openai
import spacy
from sqlalchemy.orm import Session

# Local application imports
from backend import crud, models, schemas
from backend.comet_utils import comet_tracker
from backend.database import SessionLocal, engine
from comet_ml import API
# Load Comet API key

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Initialize FastAPI app
app = FastAPI(title="Ticket_Genius - Full API with Auth")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


nlp = spacy.load("en_core_web_sm")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    comet_tracker.log_params({
        "request_method": request.method,
        "request_url": str(request.url),
        "client_host": request.client.host if request.client else None
    })
    return await call_next(request)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request metrics
        comet_tracker.log_metrics({
            "request_duration_seconds": process_time,
            "status_code": response.status_code,
            "endpoint": request.url.path
        }, step=1)
        
        return response
    except Exception as e:
        # Log error
        comet_tracker.log_metrics({
            "request_error": 1,
            "error_type": str(type(e).__name__),
            "endpoint": request.url.path
        })
        raise e

# Endpoint: POST /tickets/
@app.post("/tickets/", response_model=schemas.TicketOut)
async def create_ticket_endpoint(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    start_time = time.time()
    
    try:
        comet_tracker.start_experiment("ticket_creation")
        if ticket.user_id is None:
            raise HTTPException(status_code=400, detail="User ID must be provided.")

        comet_tracker.log_ticket({
            "title": ticket.subject,
            "description": ticket.description,
            "user_id": ticket.user_id
        })

        # Your existing ticket creation logic
        db_ticket = models.Ticket(
            user_id=ticket.user_id,
            subject=ticket.subject,
            description=ticket.description,
            status="Open",
            created_at=datetime.utcnow()
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)

        processing_time = time.time() - start_time
        comet_tracker.log_metrics({
            "processing_time_seconds": processing_time,
            "ticket_created": 1
        })

        return db_ticket

    except Exception as e:
        comet_tracker.log_metrics({
            "error": 1,
            "error_type": str(type(e).__name__)
        })
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        comet_tracker.end_experiment()

# Endpoint: GET /tickets/
@app.get("/tickets/", response_model=List[schemas.TicketOut])
def read_tickets(db: Session = Depends(get_db)):
    return crud.get_tickets(db)

# Endpoint: GET /tickets/{ticket_id}/
@app.get("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# Endpoint: PUT /tickets/{ticket_id}/
@app.put("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(ticket_id: int, update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if update.status is not None:
        ticket.status = update.status
    if update.comments is not None:
        ticket.comments = update.comments
    if update.priority is not None:
        ticket.priority = update.priority
    
    db.commit()
    db.refresh(ticket)
    return ticket

# Endpoint: DELETE /tickets/{ticket_id}/
@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted successfully"}

class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: int
    messages: List[ChatMessage]   # The full conversation: [{"role": ..., "content": ...}, ...]

class ChatHistoryEntry(BaseModel):
    response: str
    ticket_created: bool = False
    ticket_id: Optional[int] = None  # Make this field optional

@app.post("/chatbot/", response_model=ChatHistoryEntry)
def chatbot_interaction(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Initialize model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Prepare system prompt for concise answers
        system_prompt = {
            "role": "user",
            "parts": ["Answer only with concise and precise responses. Be accurate and brief."]
        }

        gemini_messages = [
            system_prompt
        ] + [
            {
                "role": "model" if msg.role == "assistant" else "user",
                "parts": [msg.content]
            }
            for msg in request.messages
        ]

        response = model.generate_content(gemini_messages)
        chatbot_response = response.text

        # Rest of your logic ...
        updated_messages = request.messages + [ChatMessage(role="assistant", content=chatbot_response)]
        #crud.save_user_chat_history(db, request.user_id, updated_messages)
        return ChatHistoryEntry(
            response=chatbot_response,
            ticket_created=False,
            ticket_id=None
        )
    except Exception as e:
        error_msg = f"Error in chatbot endpoint: {str(e)}"
        print(error_msg)
        raise HTTPException(
            status_code=500, 
            detail={"error": "Internal server error", "message": str(e)}
        )


@app.post("/process_document/")
async def process_document(file: UploadFile = File(...)):
    file_contents = await file.read()
    filename = file.filename.lower()
    if filename.endswith(".txt"):
        file_ext = "txt"
    else:
        kind = filetype.guess(file_contents)
        file_ext = kind.extension if kind else "unknown"

    extracted_text = ""
    if file_ext == "txt":
        try:
            extracted_text = file_contents.decode("utf-8")
        except Exception as e:
            extracted_text = "Text extraction failed."

    elif file_ext in ["png", "jpg", "jpeg"]:
        try:
            image = Image.open(io.BytesIO(file_contents))  
            extracted_text = extract_text_from_image(file_contents)
        except Exception as e:
            extracted_text = "OCR failed. Invalid image format."

    elif file_ext in ["pdf", "docx"]:
        try:
            extracted_text = file_contents.decode("utf-8")  
        except Exception as e:
            extracted_text = "Text extraction failed."
    else:
        return {"error": "Unsupported file type. Please upload PNG, JPG, TXT, PDF, or DOCX."}

    # Summarize and analyze sentiment using CometAPI
    # For advanced features, you need to implement these with an LLM like GPT-4o via CometAPI
    def summarize_document(text):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Summarize this document:"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content if response and hasattr(response, "choices") else ""

    def analyze_sentiment_comet(text):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this document and respond with Positive, Negative, or Neutral."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content if response and hasattr(response, "choices") else "Neutral"

    summary = summarize_document(extracted_text) if extracted_text else ""
    sentiment = analyze_sentiment_comet(extracted_text) if extracted_text else "Neutral"

    return {
        "file_type": file_ext,
        "extracted_text": extracted_text,
        "summary": summary,
        "sentiment": sentiment
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # List only needed origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all methods for development
    allow_headers=["*"],              # Allow all headers for development
)

