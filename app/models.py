from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional, Literal
from uuid import UUID
import datetime # Import datetime

class Indirizzo(BaseModel):
    via: str
    cap: str
    citta: str
    provincia: str
    nazione: str = "Italia"

class IntestazioneAzienda(BaseModel):
    nome_azienda: str
    logo_url: Optional[HttpUrl] = None
    partita_iva_azienda: str
    codice_fiscale_azienda: Optional[str] = None
    indirizzo_azienda: Indirizzo
    email_azienda: EmailStr
    telefono_azienda: Optional[str] = None
    sito_web_azienda: Optional[HttpUrl] = None

class IntestazioneCliente(BaseModel):
    nome_cliente: str
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Indirizzo
    email: Optional[EmailStr] = None
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
    data_emissione: datetime.date # Changed to datetime.date
    data_scadenza: Optional[datetime.date] = None # Changed to datetime.date
    oggetto_preventivo: str
    stato_preventivo: Literal["bozza", "inviato", "accettato", "rifiutato", "scaduto"] = "bozza"

class PreventivoMasterModel(BaseModel):
    metadati_preventivo: MetadatiPreventivo
    azienda_emittente: IntestazioneAzienda
    cliente_destinatario: IntestazioneCliente
    corpo_preventivo: TabellaPreventivo
    condizioni_contrattuali: Optional[CondizioniGenerali] = None
    dettagli_totali: SezioneTotali
    elementi_footer: Optional[FooterPreventivo] = None 