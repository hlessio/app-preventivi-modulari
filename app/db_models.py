from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import UUID # Rimuoviamo questo import per SQLite
import uuid
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(String, default="active")  # active, inactive, suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    azienda = relationship("Azienda", back_populates="proprietario", uselist=False)
    preventivi = relationship("Preventivo", back_populates="utente")

class Azienda(Base):
    __tablename__ = "aziende"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Dati azienda (corrispondenti al modello IntestazioneAzienda)
    nome_azienda = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    partita_iva_azienda = Column(String, nullable=False)
    codice_fiscale_azienda = Column(String, nullable=True)
    
    # Indirizzo (denormalizzato per semplicità)
    indirizzo_via = Column(String, nullable=False)
    indirizzo_cap = Column(String, nullable=False)
    indirizzo_citta = Column(String, nullable=False)
    indirizzo_provincia = Column(String, nullable=False)
    indirizzo_nazione = Column(String, default="Italia")
    
    email_azienda = Column(String, nullable=False)
    telefono_azienda = Column(String, nullable=True)
    sito_web_azienda = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    proprietario = relationship("User", back_populates="azienda")

class Preventivo(Base):
    __tablename__ = "preventivi"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Metadati del preventivo
    numero_preventivo = Column(String, nullable=False, index=True)
    oggetto_preventivo = Column(String, nullable=False)
    stato_preventivo = Column(String, default="bozza")  # bozza, inviato, accettato, rifiutato, scaduto
    
    # JSON Master completo del preventivo
    # Questo campo conterrà tutto il JSON come definito in PreventivoMasterModel
    dati_preventivo = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    utente = relationship("User", back_populates="preventivi") 