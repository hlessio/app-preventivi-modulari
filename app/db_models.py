from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(String(20), default="active")  # active, inactive, suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    azienda = relationship("Azienda", back_populates="proprietario", uselist=False)
    preventivi = relationship("Preventivo", back_populates="utente")

class Azienda(Base):
    __tablename__ = "aziende"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Dati azienda (corrispondenti al modello IntestazioneAzienda)
    nome_azienda = Column(String(255), nullable=False)
    logo_url = Column(String(500), nullable=True)
    partita_iva_azienda = Column(String(50), nullable=False)
    codice_fiscale_azienda = Column(String(50), nullable=True)
    
    # Indirizzo (denormalizzato per semplicità)
    indirizzo_via = Column(String(255), nullable=False)
    indirizzo_cap = Column(String(10), nullable=False)
    indirizzo_citta = Column(String(100), nullable=False)
    indirizzo_provincia = Column(String(50), nullable=False)
    indirizzo_nazione = Column(String(100), default="Italia")
    
    email_azienda = Column(String(255), nullable=False)
    telefono_azienda = Column(String(50), nullable=True)
    sito_web_azienda = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    proprietario = relationship("User", back_populates="azienda")

class Preventivo(Base):
    __tablename__ = "preventivi"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Metadati del preventivo
    numero_preventivo = Column(String(100), nullable=False, index=True)
    oggetto_preventivo = Column(String(500), nullable=False)
    stato_preventivo = Column(String(50), default="bozza")  # bozza, inviato, accettato, rifiutato, scaduto
    
    # Usa JSONB per performance e capacità di query avanzate su PostgreSQL
    dati_preventivo = Column(JSONB, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    utente = relationship("User", back_populates="preventivi") 