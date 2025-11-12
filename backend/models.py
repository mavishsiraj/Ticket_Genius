from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from backend.database import Base
from sqlalchemy.dialects.mysql import JSON

class User(Base):
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(50))  
    department = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    password = Column(String(100),nullable=False)

class Team(Base):
    __tablename__ = "teams"  
    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

class Engineer(Base):
    __tablename__ = "engineers"  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    expertise = Column(Text)  
    available = Column(String(10), default="True")  


class Ticket(Base):
    __tablename__ = "tickets"  
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    engineer_id = Column(Integer, ForeignKey("engineers.id"), nullable=True)
    subject = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="Open")
    classification = Column(String(255))
    summary = Column(Text)
    suggested_resolution = Column(Text)
    priority = Column(String(50), default="Medium")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    chat_history = Column(JSON, default=[])  # ✅ JSON column, no need for manual serialization

    def get_chat_history(self):
        return self.chat_history or []  # ✅ Directly return list (SQLAlchemy handles deserialization)

    def set_chat_history(self, history_list):
        self.chat_history = history_list  # ✅ Assign list directly (SQLAlchemy handles serialization)
