from sqlalchemy.orm import Session
from backend import models, schemas
from typing import Optional, Tuple
from passlib.context import CryptContext
from sentence_transformers import SentenceTransformer, util

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize sentence transformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def create_ticket(db: Session, ticket: schemas.TicketCreate, classification: str):
    db_ticket = models.Ticket(
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        classification=classification
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_tickets(db: Session):
    return db.query(models.Ticket).all()

def assign_team_and_engineer_db(db: Session, classification: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Uses embedding-based similarity to assign the best matching team and available engineer.
    """
    classification_embedding = embedder.encode(classification, convert_to_tensor=True)
    
    teams = db.query(models.Team).all()
    best_team = None
    best_team_score = -1  
    
    for team in teams:
        team_text = f"{team.team_name} {team.description}"
        team_embedding = embedder.encode(team_text, convert_to_tensor=True)
        score = util.cos_sim(classification_embedding, team_embedding).item()
        if score > best_team_score:
            best_team_score = score
            best_team = team

    if best_team:
        team_id = best_team.id
        engineers = db.query(models.Engineer).filter(
            models.Engineer.team_id == best_team.id,
            models.Engineer.available == "True"
        ).all()
        best_engineer = None
        best_eng_score = -1
        
        for eng in engineers:
            eng_text = eng.expertise  
            eng_embedding = embedder.encode(eng_text, convert_to_tensor=True)
            eng_score = util.cos_sim(classification_embedding, eng_embedding).item()
            if eng_score > best_eng_score:
                best_eng_score = eng_score
                best_engineer = eng
        engineer_id = best_engineer.id if best_engineer else None
    else:
        team_id = None
        engineer_id = None

    return team_id, engineer_id

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password using passlib."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a hashed password."""
    return pwd_context.hash(password)