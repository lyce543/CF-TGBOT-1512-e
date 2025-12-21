from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dialogs = relationship("Dialog", back_populates="user")

class Dialog(Base):
    __tablename__ = "dialogs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bot_name = Column(String, nullable=False)
    status = Column(String, default="новое")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="dialogs")
    messages = relationship("Message", back_populates="dialog")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    dialog_id = Column(Integer, ForeignKey("dialogs.id"))
    text = Column(Text, nullable=False)
    is_from_user = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    telegram_message_id = Column(Integer)
    
    dialog = relationship("Dialog", back_populates="messages")

class Manager(Base):
    __tablename__ = "managers"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)