from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
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
    # Nuove relazioni
    document_templates = relationship("DocumentTemplate", back_populates="user")
    user_preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    cartelle = relationship("Cartella", back_populates="user")

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
    nome_documento = Column(String(500), nullable=True)  # Nome interno del documento per organizzazione
    oggetto_preventivo = Column(String(500), nullable=False)
    stato_preventivo = Column(String(50), default="bozza")  # bozza, inviato, accettato, rifiutato, scaduto
    
    # Riferimento al template utilizzato (opzionale per backward compatibility)
    template_id = Column(UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=True)
    
    # Riferimento alla cartella (opzionale - preventivi possono non essere in nessuna cartella)
    cartella_id = Column(UUID(as_uuid=True), ForeignKey("cartelle.id"), nullable=True)
    
    # Usa JSONB per performance e capacità di query avanzate su PostgreSQL
    dati_preventivo = Column(JSONB, nullable=False)
    
    # Campi per la gestione del cestino
    stato_record = Column(String(50), default="attivo", index=True)  # es: "attivo", "cestinato"
    cestinato_il = Column(DateTime, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    utente = relationship("User", back_populates="preventivi")
    template = relationship("DocumentTemplate", back_populates="documents")
    cartella = relationship("Cartella", back_populates="preventivi")

    @hybrid_property
    def nome_cliente(self):
        if self.dati_preventivo and isinstance(self.dati_preventivo, dict):
            return self.dati_preventivo.get('cliente_destinatario', {}).get('nome_cliente')
        return None

    @hybrid_property
    def valore_totale_lordo(self):
        if self.dati_preventivo and isinstance(self.dati_preventivo, dict):
            return self.dati_preventivo.get('dettagli_totali', {}).get('totale_generale_lordo')
        return None

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informazioni template
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(100), nullable=False, default="preventivo")  # preventivo, fattura, contratto, etc.
    
    # Configurazione composizione moduli
    module_composition = Column(JSONB, nullable=False)
    
    # Configurazione formato
    page_format = Column(String(50), default="A4")  # A4, US_LETTER, A3, etc.
    page_orientation = Column(String(20), default="portrait")  # portrait, landscape
    margins = Column(JSONB, nullable=True)  # {top: 1.2, right: 0.8, bottom: 1.2, left: 0.8} in cm
    
    # CSS/Styling personalizzato (futuro)
    custom_styles = Column(Text, nullable=True)
    
    # Metadati
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Per template condivisibili
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    user = relationship("User", back_populates="document_templates")
    documents = relationship("Preventivo", back_populates="template")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    # Preferenze UI
    default_page_format = Column(String(50), default="A4")
    default_orientation = Column(String(20), default="portrait")
    preferred_language = Column(String(10), default="it")
    
    # Preferenze documento
    default_document_template_id = Column(UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=True)
    auto_save_interval = Column(Integer, default=30)  # secondi
    
    # Impostazioni privacy
    allow_public_templates = Column(Boolean, default=False)
    data_retention_days = Column(Integer, default=365)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    user = relationship("User", back_populates="user_preferences")
    default_template = relationship("DocumentTemplate", foreign_keys=[default_document_template_id])

class Cartella(Base):
    __tablename__ = "cartelle"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informazioni cartella
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text, nullable=True)
    colore = Column(String(7), nullable=True)  # Hex color (es. #FF5733)
    icona = Column(String(50), nullable=True)  # Nome dell'icona (es. 'folder', 'business', 'star')
    
    # Gerarchia (per cartelle annidate - opzionale)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("cartelle.id"), nullable=True)
    
    # Ordine personalizzato
    ordine = Column(Integer, default=0)
    
    # Metadati
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    user = relationship("User", back_populates="cartelle")
    preventivi = relationship("Preventivo", back_populates="cartella")
    
    # Auto-relazione per gerarchia
    figli = relationship("Cartella", backref="parent", remote_side=[id]) 