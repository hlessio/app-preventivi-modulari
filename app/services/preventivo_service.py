from sqlalchemy.orm import Session
from typing import List, Optional
# from uuid import UUID # Rimuoviamo l'import UUID
import uuid
from datetime import datetime, timedelta # Aggiunto timedelta

from ..db_models import Preventivo, User, Azienda, Cartella
from ..models import PreventivoMasterModel, IntestazioneAzienda, Indirizzo, PreventivoListItemConCartella

class PreventivoService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def salva_preventivo(self, preventivo_data: PreventivoMasterModel, user_id: str) -> Preventivo: # Cambiato da UUID a str
        """
        Salva un nuovo preventivo nel database.
        I nuovi preventivi sono sempre 'attivi'.
        """
        # Converti il modello Pydantic in dizionario per salvarlo come JSON
        preventivo_json = preventivo_data.model_dump(mode='json')
        
        # Crea il record del preventivo
        db_preventivo = Preventivo(
            user_id=user_id,
            numero_preventivo=preventivo_data.metadati_preventivo.numero_preventivo,
            oggetto_preventivo=preventivo_data.metadati_preventivo.oggetto_preventivo,
            stato_preventivo=preventivo_data.metadati_preventivo.stato_preventivo,
            template_id=preventivo_data.metadati_preventivo.template_id,
            dati_preventivo=preventivo_json,
            stato_record="attivo"  # Default per nuovi preventivi
        )
        
        self.db.add(db_preventivo)
        self.db.commit()
        self.db.refresh(db_preventivo)
        
        return db_preventivo
    
    def aggiorna_preventivo(self, preventivo_id: str, preventivo_data: PreventivoMasterModel, user_id: str) -> Optional[Preventivo]: # Cambiato da UUID a str
        """
        Aggiorna un preventivo esistente.
        Solo i preventivi attivi possono essere aggiornati tramite questo metodo.
        """
        # Trova il preventivo attivo
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "attivo" # Aggiunto filtro per stato_record
        ).first()
        
        if not db_preventivo:
            return None
        
        # Aggiorna i dati
        preventivo_json = preventivo_data.model_dump(mode='json')
        db_preventivo.numero_preventivo = preventivo_data.metadati_preventivo.numero_preventivo
        db_preventivo.oggetto_preventivo = preventivo_data.metadati_preventivo.oggetto_preventivo
        db_preventivo.stato_preventivo = preventivo_data.metadati_preventivo.stato_preventivo
        db_preventivo.template_id = preventivo_data.metadati_preventivo.template_id
        db_preventivo.dati_preventivo = preventivo_json
        db_preventivo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_preventivo)
        
        return db_preventivo
    
    def carica_preventivo(self, preventivo_id: str, user_id: str, solo_attivi: bool = True) -> Optional[PreventivoMasterModel]: # Cambiato da UUID a str
        """
        Carica un preventivo dal database e lo converte in PreventivoMasterModel.
        Di default carica solo preventivi attivi, ma può caricarli anche se cestinati se solo_attivi=False.
        """
        query = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
        )
        if solo_attivi:
            query = query.filter(Preventivo.stato_record == "attivo")
        
        db_preventivo = query.first()
        
        if not db_preventivo:
            return None
        
        # Converte il JSON in PreventivoMasterModel
        try:
            # Inizia con il dizionario JSON memorizzato
            preventivo_dati_dict = db_preventivo.dati_preventivo
            
            # Assicurati che 'metadati_preventivo' esista come dizionario
            # e che preventivo_dati_dict sia effettivamente un dizionario
            if not isinstance(preventivo_dati_dict, dict):
                # Questo non dovrebbe accadere se dati_preventivo è sempre un JSON valido
                print(f"Attenzione: dati_preventivo per {preventivo_id} non è un dict come atteso.")
                preventivo_dati_dict = {} # Fallback per evitare errori ulteriori

            if not isinstance(preventivo_dati_dict.get('metadati_preventivo'), dict):
                preventivo_dati_dict['metadati_preventivo'] = {}

            # Imposta o sovrascrivi il template_id nei dati con quello dalla colonna del DB
            # Converti l'UUID in stringa se presente, altrimenti None
            preventivo_dati_dict['metadati_preventivo']['template_id'] = str(db_preventivo.template_id) if db_preventivo.template_id else None
            
            # Ora crea il PreventivoMasterModel usando il dizionario aggiornato
            preventivo_model = PreventivoMasterModel(**preventivo_dati_dict)
            # Potremmo voler arricchire il modello con lo stato_record se necessario al chiamante
            return preventivo_model
        except Exception as e:
            # Log dell'errore
            print(f"Errore nella deserializzazione del preventivo {preventivo_id}: {e}")
            return None
    
    def lista_preventivi_attivi(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Preventivo]:
        """
        Restituisce la lista dei preventivi attivi per un utente.
        """
        return self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "attivo"
        ).order_by(Preventivo.updated_at.desc()).offset(skip).limit(limit).all()

    def lista_preventivi_cestinati(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Preventivo]:
        """
        Restituisce la lista dei preventivi cestinati per un utente.
        """
        return self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "cestinato"
        ).order_by(Preventivo.cestinato_il.desc()).offset(skip).limit(limit).all()

    def cestina_preventivo(self, preventivo_id: str, user_id: str) -> Optional[Preventivo]:
        """
        Sposta un preventivo nel cestino (soft delete).
        """
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "attivo" # Solo i preventivi attivi possono essere cestinati
        ).first()
        
        if not db_preventivo:
            return None # O solleva un'eccezione
        
        db_preventivo.stato_record = "cestinato"
        db_preventivo.cestinato_il = datetime.utcnow()
        db_preventivo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_preventivo)
        return db_preventivo

    def ripristina_preventivo(self, preventivo_id: str, user_id: str) -> Optional[Preventivo]:
        """
        Ripristina un preventivo dal cestino.
        """
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "cestinato" # Solo i preventivi cestinati possono essere ripristinati
        ).first()
        
        if not db_preventivo:
            return None # O solleva un'eccezione
        
        db_preventivo.stato_record = "attivo"
        db_preventivo.cestinato_il = None
        db_preventivo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_preventivo)
        return db_preventivo

    def elimina_definitivamente_preventivo(self, preventivo_id: str, user_id: str) -> bool:
        """
        Elimina definitivamente un preventivo dal database.
        Tipicamente usato per preventivi già nel cestino.
        """
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
            # Considerare se permettere l'eliminazione definitiva solo se 'cestinato'
            # Preventivo.stato_record == "cestinato" 
        ).first()
        
        if not db_preventivo:
            return False
        
        self.db.delete(db_preventivo)
        self.db.commit()
        
        return True

    def svuota_cestino_scaduti(self, user_id: Optional[str] = None, giorni_scadenza: int = 30) -> int:
        """
        Elimina definitivamente i preventivi cestinati da più di 'giorni_scadenza'.
        Se user_id è fornito, opera solo per quell'utente.
        Altrimenti (con cautela!), potrebbe operare globalmente (richiede privilegi admin non implementati qui).
        Restituisce il numero di preventivi eliminati.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=giorni_scadenza)
        query = self.db.query(Preventivo).filter(
            Preventivo.stato_record == "cestinato",
            Preventivo.cestinato_il <= cutoff_date
        )
        
        if user_id:
            query = query.filter(Preventivo.user_id == user_id)
        else:
            # Qui si potrebbe inserire un controllo per ruolo admin se si volesse un cleanup globale
            # Per ora, se user_id non è fornito, non fa nulla per sicurezza.
            # O, si potrebbe decidere che questa funzione è sempre per utente.
            # In un sistema multi-tenant reale, il cleanup globale sarebbe più complesso.
            print("Attenzione: user_id non fornito per svuota_cestino_scaduti. Nessuna operazione globale eseguita per sicurezza.")
            return 0


        preventivi_da_eliminare = query.all()
        count = len(preventivi_da_eliminare)
        
        if count > 0:
            for preventivo in preventivi_da_eliminare:
                self.db.delete(preventivo)
            self.db.commit()
            
        return count

    def svuota_tutto_cestino(self, user_id: str) -> int:
        """
        Elimina definitivamente TUTTI i preventivi nel cestino per un utente.
        Restituisce il numero di preventivi eliminati.
        """
        query = self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id,
            Preventivo.stato_record == "cestinato"
        )
        
        preventivi_da_eliminare = query.all()
        count = len(preventivi_da_eliminare)
        
        if count > 0:
            for preventivo in preventivi_da_eliminare:
                self.db.delete(preventivo)
            self.db.commit()
            
        return count

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

    def lista_preventivi_con_cartelle(self, user_id: str, stato_record: str = "attivo", cartella_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[PreventivoListItemConCartella]:
        """
        Restituisce la lista dei preventivi con informazioni delle cartelle.
        Se cartella_id è specificato, filtra per quella cartella.
        Se cartella_id è 'none', filtra per preventivi senza cartella.
        """
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id,
            Preventivo.stato_record == stato_record
        ).outerjoin(Cartella, Preventivo.cartella_id == Cartella.id)
        
        # Filtro per cartella se specificato
        if cartella_id == 'none':
            query = query.filter(Preventivo.cartella_id.is_(None))
        elif cartella_id:
            query = query.filter(Preventivo.cartella_id == cartella_id)
        
        # Aggiungi le colonne della cartella alla query
        query = query.add_columns(
            Cartella.nome.label('cartella_nome'),
            Cartella.colore.label('cartella_colore')
        )
        
        preventivi = query.order_by(Preventivo.updated_at.desc()).offset(skip).limit(limit).all()
        
        # Converti in PreventivoListItemConCartella
        result = []
        for row in preventivi: # Rinominato item in row per chiarezza
            preventivo_obj = row[0]    # L'oggetto Preventivo è sempre il primo elemento
            cartella_nome_val = row[1] # Valore da Cartella.nome.label('cartella_nome')
            cartella_colore_val = row[2]# Valore da Cartella.colore.label('cartella_colore')
            
            result.append(PreventivoListItemConCartella(
                id=str(preventivo_obj.id),
                numero_preventivo=preventivo_obj.numero_preventivo,
                oggetto_preventivo=preventivo_obj.oggetto_preventivo,
                stato_preventivo=preventivo_obj.stato_preventivo,
                nome_cliente=preventivo_obj.nome_cliente,
                valore_totale_lordo=preventivo_obj.valore_totale_lordo,
                created_at=preventivo_obj.created_at,
                updated_at=preventivo_obj.updated_at,
                stato_record=preventivo_obj.stato_record,
                cestinato_il=preventivo_obj.cestinato_il,
                cartella_id=str(preventivo_obj.cartella_id) if preventivo_obj.cartella_id else None,
                cartella_nome=cartella_nome_val,
                cartella_colore=cartella_colore_val
            ))
        
        return result

    def sposta_preventivo_in_cartella(self, preventivo_id: str, user_id: str, cartella_id: Optional[str] = None) -> Optional[Preventivo]:
        """
        Sposta un preventivo in una cartella (o lo rimuove da una cartella se cartella_id è None).
        """
        # Trova il preventivo
        db_preventivo = self.db.query(Preventivo).filter(
            Preventivo.id == preventivo_id,
            Preventivo.user_id == user_id
        ).first()
        
        if not db_preventivo:
            return None
        
        # Verifica che la cartella esista (se specificata)
        if cartella_id:
            cartella = self.db.query(Cartella).filter(
                Cartella.id == cartella_id,
                Cartella.user_id == user_id
            ).first()
            if not cartella:
                raise ValueError("Cartella non trovata")
        
        # Aggiorna la cartella del preventivo
        db_preventivo.cartella_id = cartella_id
        db_preventivo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_preventivo)
        
        return db_preventivo 