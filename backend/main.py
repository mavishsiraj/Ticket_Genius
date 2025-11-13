# Standard library imports
import io
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Third-party imports
from dotenv import load_dotenv
from fastapi import (
    Depends, FastAPI, File, HTTPException,
    Request, UploadFile
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from PIL import Image
from pydantic import BaseModel
import filetype
import spacy
from sqlalchemy.orm import Session
import google.generativeai as genai

# Local imports
from backend import crud, models, schemas
from backend.database import SessionLocal, engine
from .ocr_utils import extract_text_from_image

# Load environment
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI
app = FastAPI(title="Ticket_Genius - Full API with Auth")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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

# -------------------------------------------------------------------
# Ticket Endpoints
# -------------------------------------------------------------------

@app.post("/tickets/", response_model=schemas.TicketOut)
async def create_ticket_endpoint(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    try:
        if ticket.user_id is None:
            raise HTTPException(status_code=400, detail="User ID must be provided.")

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

        return db_ticket

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tickets/", response_model=List[schemas.TicketOut])
def read_tickets(db: Session = Depends(get_db)):
    return crud.get_tickets(db)


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


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


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted successfully"}

# -------------------------------------------------------------------
# Chatbot (Gemini)
# -------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: int
    messages: List[ChatMessage]


class ChatHistoryEntry(BaseModel):
    response: str
    ticket_created: bool = False
    ticket_id: Optional[int] = None


@app.post("/chatbot/", response_model=ChatHistoryEntry)
def chatbot_interaction(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

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

        return ChatHistoryEntry(
            response=chatbot_response,
            ticket_created=False,
            ticket_id=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )

# -------------------------------------------------------------------
# Document Processing (Gemini)
# -------------------------------------------------------------------

@app.post("/process_document/")
async def process_document(file: UploadFile = File(...)):
    file_contents = await file.read()
    filename = file.filename.lower()

    # Determine file type
    if filename.endswith(".txt"):
        file_ext = "txt"
    else:
        guess = filetype.guess(file_contents)
        file_ext = guess.extension if guess else "unknown"

    extracted_text = ""

    # Extract text
    if file_ext == "txt":
        try:
            extracted_text = file_contents.decode("utf-8")
        except:
            extracted_text = "Text extraction failed."

    elif file_ext in ["png", "jpg", "jpeg"]:
        try:
            extracted_text = extract_text_from_image(file_contents)
        except:
            extracted_text = "OCR failed. Invalid image format."

    elif file_ext in ["pdf", "docx"]:
        try:
            extracted_text = file_contents.decode("utf-8", errors="ignore")
        except:
            extracted_text = "Text extraction failed."

    else:
        return {"error": "Unsupported file type. Please upload PNG, JPG, TXT, PDF, or DOCX."}

    # Summarization (Gemini)
    def summarize_document(text):
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            f"Summarize the following document briefly and clearly:\n\n{text}"
        )
        return response.text.strip()

    # Sentiment Analysis (Gemini)
    def analyze_sentiment_comet(text):
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            f"Analyze the sentiment of this text. Respond ONLY with: Positive, Negative, or Neutral.\n\n{text}"
        )
        return response.text.strip()

    summary = summarize_document(extracted_text)
    sentiment = analyze_sentiment_comet(extracted_text)

    return {
        "file_type": file_ext,
        "extracted_text": extracted_text,
        "summary": summary,
        "sentiment": sentiment
    }
