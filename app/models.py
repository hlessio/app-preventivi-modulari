from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
import datetime # Import datetime

class Indirizzo(BaseModel):
    via: str
    cap: Optional[str] = ""
    citta: Optional[str] = ""
    provincia: Optional[str] = ""
    nazione: str = "Italia"

class IntestazioneAzienda(BaseModel):
    nome_azienda: str
    logo_url: Optional[HttpUrl] = None
    partita_iva_azienda: str
    codice_fiscale_azienda: Optional[str] = None
    indirizzo_azienda: Indirizzo
    email_azienda: str
    telefono_azienda: Optional[str] = None
    sito_web_azienda: Optional[HttpUrl] = None

class IntestazioneCliente(BaseModel):
    nome_cliente: str
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Indirizzo
    email: Optional[str] = None
    telefono: Optional[str] = None
    referente: Optional[str] = None

class RigaPreventivo(BaseModel):
    numero_riga: Optional[int] = Field(default=None, readOnly=True)
    codice_articolo: Optional[str] = None
    descrizione: str
    unita_misura: str = "pz"
    quantita: float = 1
    prezzo_unitario_netto: float
    percentuale_iva: float = 22
    importo_iva_riga: Optional[float] = Field(default=None, readOnly=True)
    subtotale_riga_netto: Optional[float] = Field(default=None, readOnly=True)
    subtotale_riga_lordo: Optional[float] = Field(default=None, readOnly=True)
    sconto_riga_percentuale: Optional[float] = 0
    note_riga: Optional[str] = None

class TabellaPreventivo(BaseModel):
    righe: List[RigaPreventivo] = []
    note_tabella: Optional[str] = None

class CondizioniGenerali(BaseModel):
    testo_condizioni: str

class FooterPreventivo(BaseModel):
    dati_pagamento: Optional[str] = None
    validita_preventivo: Optional[str] = None
    note_finali: Optional[str] = None
    firma_azienda: Optional[str] = None

class RiepilogoIVA(BaseModel):
    aliquota_percentuale: float
    imponibile_aliquota: float
    iva_aliquota: float

class SezioneTotali(BaseModel):
    totale_imponibile_netto: float = Field(..., readOnly=True)
    totale_sconti: Optional[float] = Field(default=None, readOnly=True)
    totale_iva: float = Field(..., readOnly=True)
    totale_generale_lordo: float = Field(..., readOnly=True)
    riepilogo_iva: Optional[List[RiepilogoIVA]] = Field(default=None, readOnly=True)

class MetadatiPreventivo(BaseModel):
    id_preventivo: UUID
    numero_preventivo: str
    nome_documento: Optional[str] = Field(None, description="Nome interno del documento per organizzazione")
    data_emissione: datetime.date # Changed to datetime.date
    data_scadenza: Optional[datetime.date] = None # Changed to datetime.date
    oggetto_preventivo: str
    stato_preventivo: Literal["bozza", "inviato", "accettato", "rifiutato", "scaduto"] = "bozza"
    template_id: Optional[str] = None  # ID del template utilizzato

class PreventivoMasterModel(BaseModel):
    metadati_preventivo: MetadatiPreventivo
    azienda_emittente: IntestazioneAzienda
    cliente_destinatario: IntestazioneCliente
    corpo_preventivo: TabellaPreventivo
    condizioni_contrattuali: Optional[CondizioniGenerali] = None
    dettagli_totali: SezioneTotali
    elementi_footer: Optional[FooterPreventivo] = None

# Modello per la visualizzazione sintetica dei preventivi in una lista
class PreventivoListItem(BaseModel):
    id: UUID
    numero_preventivo: str
    nome_documento: Optional[str] = None
    oggetto_preventivo: str
    stato_preventivo: str # Lo stato funzionale (bozza, inviato, etc.)
    stato_record: Optional[str] = None # Lo stato del record (attivo, cestinato)
    nome_cliente: Optional[str] = None
    valore_totale_lordo: Optional[float] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    cestinato_il: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True # Per Pydantic V2 (sostituisce orm_mode)

# ============================================
# TEMPLATE DOCUMENTI E PREFERENZE UTENTE
# ============================================

class ModuleConfig(BaseModel):
    module_name: str = Field(..., description="Nome del modulo (es. 'intestazione_azienda')")
    order: int = Field(..., description="Ordine di visualizzazione del modulo")
    enabled: bool = Field(True, description="Se il modulo è abilitato")
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Configurazioni personalizzate del modulo")

class ModuleComposition(BaseModel):
    modules: List[ModuleConfig] = Field(..., description="Lista ordinata dei moduli")

class DocumentTemplateCreate(BaseModel):
    name: str = Field(..., max_length=255, description="Nome del template")
    description: Optional[str] = Field(None, description="Descrizione del template")
    document_type: str = Field("preventivo", max_length=100, description="Tipo di documento")
    module_composition: ModuleComposition = Field(..., description="Configurazione composizione moduli")
    page_format: str = Field("A4", max_length=50, description="Formato pagina")
    page_orientation: str = Field("portrait", max_length=20, description="Orientamento pagina")
    margins: Optional[Dict[str, float]] = Field(None, description="Margini in cm")
    custom_styles: Optional[str] = Field(None, description="CSS personalizzato")
    is_default: bool = Field(False, description="Template di default")
    is_public: bool = Field(False, description="Template pubblico")

class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    module_composition: Optional[ModuleComposition] = Field(None)
    page_format: Optional[str] = Field(None, max_length=50)
    page_orientation: Optional[str] = Field(None, max_length=20)
    margins: Optional[Dict[str, float]] = Field(None)
    custom_styles: Optional[str] = Field(None)
    is_default: Optional[bool] = Field(None)
    is_public: Optional[bool] = Field(None)

class DocumentTemplateResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    document_type: str
    module_composition: ModuleComposition
    page_format: str
    page_orientation: str
    margins: Optional[Dict[str, float]]
    custom_styles: Optional[str]
    is_default: bool
    is_public: bool
    version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class UserPreferencesCreate(BaseModel):
    default_page_format: str = Field("A4", max_length=50)
    default_orientation: str = Field("portrait", max_length=20)
    preferred_language: str = Field("it", max_length=10)
    default_document_template_id: Optional[str] = Field(None)
    auto_save_interval: int = Field(30, description="Intervallo auto-salvataggio in secondi")
    allow_public_templates: bool = Field(False)
    data_retention_days: int = Field(365)

class UserPreferencesUpdate(BaseModel):
    default_page_format: Optional[str] = Field(None, max_length=50)
    default_orientation: Optional[str] = Field(None, max_length=20)
    preferred_language: Optional[str] = Field(None, max_length=10)
    default_document_template_id: Optional[str] = Field(None)
    auto_save_interval: Optional[int] = Field(None)
    allow_public_templates: Optional[bool] = Field(None)
    data_retention_days: Optional[int] = Field(None)

class UserPreferencesResponse(BaseModel):
    user_id: str
    default_page_format: str
    default_orientation: str
    preferred_language: str
    default_document_template_id: Optional[str]
    auto_save_interval: int
    allow_public_templates: bool
    data_retention_days: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# ================================
# MODELLI CARTELLE
# ================================

class CartellaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome della cartella")
    descrizione: Optional[str] = Field(None, max_length=1000, description="Descrizione opzionale della cartella")
    colore: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Colore esadecimale (es. #FF5733)")
    icona: Optional[str] = Field(None, max_length=50, description="Nome dell'icona")
    parent_id: Optional[str] = Field(None, description="ID della cartella padre (per cartelle annidate)")
    ordine: int = Field(0, description="Ordine di visualizzazione")

class CartellaCreate(CartellaBase):
    pass

class CartellaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    colore: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icona: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[str] = None
    ordine: Optional[int] = None

class CartellaResponse(CartellaBase):
    id: str
    user_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    numero_preventivi: int = Field(0, description="Numero di preventivi nella cartella")
    
    class Config:
        from_attributes = True

class CartellaSpostamento(BaseModel):
    preventivo_ids: List[str] = Field(..., description="Lista di ID preventivi da spostare")
    cartella_id: Optional[str] = Field(None, description="ID cartella destinazione (None per rimuovere dalla cartella)")

# ================================
# MODELLI PREVENTIVO CON CARTELLE
# ================================

class PreventivoListItemConCartella(BaseModel):
    id: str
    numero_preventivo: str
    nome_documento: Optional[str] = None
    oggetto_preventivo: str
    stato_preventivo: str
    nome_cliente: Optional[str] = None
    valore_totale_lordo: Optional[float] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    stato_record: str
    cestinato_il: Optional[datetime.datetime] = None
    cartella_id: Optional[str] = None
    cartella_nome: Optional[str] = None
    cartella_colore: Optional[str] = None
    
    class Config:
        from_attributes = True 