from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    company = Column(String)
    companyType = Column(String)
    companySize = Column(String)
    role = Column(String)
    phone = Column(String)
    country = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    
    feedbacks = relationship("Feedback", back_populates="owner")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_text = Column(String, nullable=False)
    sentiment_label = Column(String)
    sentiment_prob = Column(Float)
    urgency_label = Column(String)
    urgency_prob = Column(Float)
    priority_action = Column(String)
    domain = Column(String, default="general")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="feedbacks")

