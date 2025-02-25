from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend import models, schemas, crud
from backend.database import SessionLocal, engine
from backend.openai_utils import get_dynamic_resolution_gemini
from backend.ocr_utils import extract_text_from_image
from backend.openai_utils import summarize_text_gemini
from backend.openai_utils import analyze_sentiment_gemini
from backend.crud  import assign_team_and_engineer_db  
from backend.openai_utils import classify_ticket_gemini
from backend.crud import assign_team_and_engineer_db
from backend.crud import verify_password  
from backend.openai_utils import summarize_document
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError 
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  
from . import schemas
from PIL import Image  
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import io  
import spacy
import filetype
from typing import List
from pydantic import BaseModel
import google.generativeai as genai

genai.configure(api_key="AIzaSyAqMpaEuREHoFNck8FkXnjvN8zRDjrY9lc") 
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Ticket_Genius - Full API with Auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

nlp = spacy.load("en_core_web_sm")
"""
def create_access_token(data: dict, expires_delta: timedelta):  
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"sub": str(to_encode["sub"])})  
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        print("Received Token:", token)  # Debugging line
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded Payload:", payload)  # Debugging line
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        print("JWT Error:", e)  # Debugging line
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    return payload

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.id}, timedelta(hours=2))  

    return {"access_token": access_token, "token_type": "bearer"}
"""

# Endpoint: POST /tickets/
@app.post("/tickets/", response_model=schemas.TicketOut)
def create_ticket_endpoint(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    if ticket.user_id is None:
        raise HTTPException(status_code=400, detail="User ID must be provided.")
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found with provided ID.")
    try:
        
        classification = classify_ticket_gemini(ticket.description)
        summary = summarize_text_gemini(ticket.description)
        suggested_resolution = get_dynamic_resolution_gemini(ticket.description)
        team_id, engineer_id = assign_team_and_engineer_db(db, classification)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")
    
    db_ticket = crud.create_ticket(db, ticket, classification)
    db_ticket.summary = summary
    db_ticket.user_id = ticket.user_id
    db_ticket.suggested_resolution = suggested_resolution
    db_ticket.team_id = team_id
    db_ticket.engineer_id = engineer_id
    db_ticket.suggested_resolution = suggested_resolution
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

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

class ChatRequest(BaseModel):
    query: str
    user_id: int
    history: list[str] = []  

@app.post("/chatbot/")
def chatbot_interaction(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        model = genai.GenerativeModel("gemini-pro")
        messages = [{"role": "user", "content": q} for q in request.history]
        messages.append({"role": "user", "content": request.query})

        response = model.generate_content(request.query)
        chatbot_response = response.text.strip() if response and hasattr(response, "text") else "No valid response."

        if "unable to resolve" in chatbot_response.lower() or "please contact support" in chatbot_response.lower():
            ticket = models.Ticket(
                user_id=request.user_id,
                subject="Chatbot Unresolved Issue",
                description=request.query,
                classification="Unresolved",
                suggested_resolution=chatbot_response
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)

            return {
                "response": chatbot_response,
                "ticket_created": True,
                "ticket_id": ticket.id
            }

        return {"response": chatbot_response, "ticket_created": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

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

    summary = summarize_document(extracted_text) if extracted_text else ""
    sentiment = analyze_sentiment_gemini(extracted_text) if extracted_text else "Neutral"

    return {
        "file_type": file_ext,
        "extracted_text": extracted_text,
        "summary": summary,
        "sentiment": sentiment
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "https://yourfrontend.com"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  
    allow_headers=["Content-Type", "Authorization"],  
)

