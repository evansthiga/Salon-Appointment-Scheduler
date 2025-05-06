from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from config import DATABASE_URL

Base = declarative_base()

class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="client")

class Stylist(Base):
    __tablename__ = 'stylists'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    specialties = Column(String(500))  # Comma-separated list of services
    active = Column(Boolean, default=True)
    appointments = relationship("Appointment", back_populates="stylist")

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    duration = Column(Integer, nullable=False)  # in minutes
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    stylist_id = Column(Integer, ForeignKey('stylists.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="appointments")
    stylist = relationship("Stylist", back_populates="appointments")
    service = relationship("Service")

class EmailLog(Base):
    __tablename__ = 'email_logs'

    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    email_type = Column(String(50))  # acknowledgment, confirmation, reminder, etc.
    recipient = Column(String(120), nullable=False)
    subject = Column(String(200))
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20))  # sent, failed, etc.

# Create database and tables
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine) 