from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TicketCreate(BaseModel):
    user_id: int
    subject: str
    description: str

class TicketOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    subject: str
    description: str
    status: str
    classification: Optional[str] = None
    summary: Optional[str] = None
    suggested_resolution: Optional[str] = None
    assigned_team_name: Optional[str] = None
    assigned_engineer_name: Optional[str] = None
    priority: Optional[str] = "Medium"  
    created_at: datetime

    

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    classification: Optional[str] = None
    summary: Optional[str] = None
    suggested_resolution: Optional[str] = None
    assigned_team: Optional[str] = None
    priority: Optional[str] = None  

    model_config = ConfigDict(from_attributes=True)
