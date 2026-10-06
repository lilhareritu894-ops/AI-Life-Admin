from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.base import Base

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    due_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    doc_type = Column(String, nullable=True)
    extracted_text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CalendarEventModel(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    status = Column(String, default="Scheduled")