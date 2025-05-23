from sqlalchemy.orm import Session
from typing import List, Optional
# from uuid import UUID # Rimuoviamo l'import UUID
import uuid
from datetime import datetime

from ..db_models import Preventivo, User, Azienda
from ..models import PreventivoMasterModel, IntestazioneAzienda, Indirizzo

class PreventivoService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def salva_preventivo(self, preventivo_data: PreventivoMasterModel, user_id: str) -> Preventivo: # Cambiato da UUID a str
        """
        Salva un nuovo preventivo nel database.
        """
        # Converti il modello Pydantic in dizionario per salvarlo come JSON
        preventivo_json = preventivo_data.model_dump()
        
        # Crea il record del preventivo
        db_preventivo = Preventivo(
            user_id=user_id,
            numero_preventivo=preventivo_data.metadati_preventivo.numero_preventivo,
            oggetto_preventivo=preventivo_data.metadati_preventivo.oggetto_preventivo,
            stato_preventivo=preventivo_data.metadati_preventivo.stato_preventivo,
            dati_preventivo=preventivo_json
        )
        
        self.db.add(db_preventivo)
        self.db.commit()
        self.db.refresh(db_preventivo)
        
        return db_preventivo
    
    def aggiorna_preventivo(self, preventivo_id: str, preventivo_data: PreventivoMasterModel, user_id: str) -> Optional[Preventivo]: # Cambiato da UUID a str
        """
        Aggiorna un preventivo esistente.
        """
        # Trova il preventivo
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
        ).first()
        
        if not db_preventivo:
            return None
        
        # Aggiorna i dati
        preventivo_json = preventivo_data.model_dump()
        db_preventivo.numero_preventivo = preventivo_data.metadati_preventivo.numero_preventivo
        db_preventivo.oggetto_preventivo = preventivo_data.metadati_preventivo.oggetto_preventivo
        db_preventivo.stato_preventivo = preventivo_data.metadati_preventivo.stato_preventivo
        db_preventivo.dati_preventivo = preventivo_json
        db_preventivo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_preventivo)
        
        return db_preventivo
    
    def carica_preventivo(self, preventivo_id: str, user_id: str) -> Optional[PreventivoMasterModel]: # Cambiato da UUID a str
        """
        Carica un preventivo dal database e lo converte in PreventivoMasterModel.
        """
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
        ).first()
        
        if not db_preventivo:
            return None
        
        # Converte il JSON in PreventivoMasterModel
        try:
            preventivo_model = PreventivoMasterModel(**db_preventivo.dati_preventivo)
            return preventivo_model
        except Exception as e:
            # Log dell'errore
            print(f"Errore nella deserializzazione del preventivo {preventivo_id}: {e}")
            return None
    
    def lista_preventivi(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Preventivo]: # Cambiato da UUID a str
        """
        Restituisce la lista dei preventivi per un utente.
        """
        return self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def elimina_preventivo(self, preventivo_id: str, user_id: str) -> bool: # Cambiato da UUID a str
        """
        Elimina un preventivo.
        """
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
        ).first()
        
        if not db_preventivo:
            return False
        
        self.db.delete(db_preventivo)
        self.db.commit()
        
        return True
    
    def get_dati_azienda_utente(self, user_id: str) -> Optional[IntestazioneAzienda]: # Cambiato da UUID a str
        """
        Recupera i dati dell'azienda per un utente e li converte in IntestazioneAzienda.
        """
        azienda = self.db.query(Azienda).filter(Azienda.user_id == user_id).first()
        
        if not azienda:
            return None
        
        # Converte i dati dell'azienda nel modello Pydantic
        indirizzo = Indirizzo(
            via=azienda.indirizzo_via,
            cap=azienda.indirizzo_cap,
            citta=azienda.indirizzo_citta,
            provincia=azienda.indirizzo_provincia,
            nazione=azienda.indirizzo_nazione
        )
        
        intestazione_azienda = IntestazioneAzienda(
            nome_azienda=azienda.nome_azienda,
            logo_url=azienda.logo_url,
            partita_iva_azienda=azienda.partita_iva_azienda,
            codice_fiscale_azienda=azienda.codice_fiscale_azienda,
            indirizzo_azienda=indirizzo,
            email_azienda=azienda.email_azienda,
            telefono_azienda=azienda.telefono_azienda,
            sito_web_azienda=azienda.sito_web_azienda
        )
        
        return intestazione_azienda 