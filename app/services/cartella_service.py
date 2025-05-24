from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uuid
from datetime import datetime

from ..db_models import Cartella, Preventivo, User
from ..models import CartellaCreate, CartellaUpdate, CartellaResponse, CartellaSpostamento

class CartellaService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def crea_cartella(self, cartella_data: CartellaCreate, user_id: str) -> Cartella:
        """
        Crea una nuova cartella per l'utente.
        """
        # Verifica che l'utente esista
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Utente non trovato")
        
        # Verifica che la cartella padre esista (se specificata)
        if cartella_data.parent_id:
            parent = self.db.query(Cartella).filter(
                Cartella.id == cartella_data.parent_id,
                Cartella.user_id == user_id
            ).first()
            if not parent:
                raise ValueError("Cartella padre non trovata")
        
        # Crea la nuova cartella
        db_cartella = Cartella(
            user_id=user_id,
            nome=cartella_data.nome,
            descrizione=cartella_data.descrizione,
            colore=cartella_data.colore,
            icona=cartella_data.icona,
            parent_id=cartella_data.parent_id,
            ordine=cartella_data.ordine
        )
        
        self.db.add(db_cartella)
        self.db.commit()
        self.db.refresh(db_cartella)
        
        return db_cartella
    
    def lista_cartelle(self, user_id: str, includi_conteggi: bool = True) -> List[CartellaResponse]:
        """
        Restituisce tutte le cartelle dell'utente con conteggio preventivi.
        """
        query = self.db.query(Cartella).filter(Cartella.user_id == user_id)
        
        if includi_conteggi:
            # Join con conteggio preventivi attivi
            query = query.outerjoin(
                Preventivo, 
                (Preventivo.cartella_id == Cartella.id) & 
                (Preventivo.stato_record == "attivo")
            ).add_columns(
                func.count(Preventivo.id).label('numero_preventivi')
            ).group_by(Cartella.id)
        
        cartelle = query.order_by(Cartella.ordine, Cartella.nome).all()
        
        if includi_conteggi:
            return [
                CartellaResponse(
                    id=str(cartella.Cartella.id),
                    user_id=str(cartella.Cartella.user_id),
                    nome=cartella.Cartella.nome,
                    descrizione=cartella.Cartella.descrizione,
                    colore=cartella.Cartella.colore,
                    icona=cartella.Cartella.icona,
                    parent_id=str(cartella.Cartella.parent_id) if cartella.Cartella.parent_id else None,
                    ordine=cartella.Cartella.ordine,
                    created_at=cartella.Cartella.created_at,
                    updated_at=cartella.Cartella.updated_at,
                    numero_preventivi=cartella.numero_preventivi or 0
                )
                for cartella in cartelle
            ]
        else:
            return [
                CartellaResponse(
                    id=str(cartella.id),
                    user_id=str(cartella.user_id),
                    nome=cartella.nome,
                    descrizione=cartella.descrizione,
                    colore=cartella.colore,
                    icona=cartella.icona,
                    parent_id=str(cartella.parent_id) if cartella.parent_id else None,
                    ordine=cartella.ordine,
                    created_at=cartella.created_at,
                    updated_at=cartella.updated_at,
                    numero_preventivi=0
                )
                for cartella in cartelle
            ]
    
    def ottieni_cartella(self, cartella_id: str, user_id: str) -> Optional[Cartella]:
        """
        Ottiene una cartella specifica dell'utente.
        """
        return self.db.query(Cartella).filter(
            Cartella.id == cartella_id,
            Cartella.user_id == user_id
        ).first()
    
    def aggiorna_cartella(self, cartella_id: str, cartella_data: CartellaUpdate, user_id: str) -> Optional[Cartella]:
        """
        Aggiorna una cartella esistente.
        """
        db_cartella = self.ottieni_cartella(cartella_id, user_id)
        if not db_cartella:
            return None
        
        # Aggiorna solo i campi forniti
        update_data = cartella_data.model_dump(exclude_unset=True)
        
        # Verifica cartella padre se specificata
        if 'parent_id' in update_data and update_data['parent_id']:
            parent = self.db.query(Cartella).filter(
                Cartella.id == update_data['parent_id'],
                Cartella.user_id == user_id
            ).first()
            if not parent:
                raise ValueError("Cartella padre non trovata")
            
            # Previeni cicli (cartella non può essere figlia di se stessa o di sue discendenti)
            if self._crea_ciclo(cartella_id, update_data['parent_id'], user_id):
                raise ValueError("Operazione non consentita: creerebbe un ciclo nella gerarchia")
        
        for field, value in update_data.items():
            setattr(db_cartella, field, value)
        
        db_cartella.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_cartella)
        
        return db_cartella
    
    def elimina_cartella(self, cartella_id: str, user_id: str, sposta_preventivi_a: Optional[str] = None) -> bool:
        """
        Elimina una cartella. 
        I preventivi possono essere spostati in un'altra cartella o rimanere senza cartella.
        """
        db_cartella = self.ottieni_cartella(cartella_id, user_id)
        if not db_cartella:
            return False
        
        # Sposta i preventivi se richiesto
        if sposta_preventivi_a:
            # Verifica che la cartella di destinazione esista
            cartella_destinazione = self.ottieni_cartella(sposta_preventivi_a, user_id)
            if not cartella_destinazione:
                raise ValueError("Cartella di destinazione non trovata")
            
            self.db.query(Preventivo).filter(
                Preventivo.cartella_id == cartella_id
            ).update({Preventivo.cartella_id: sposta_preventivi_a})
        else:
            # Rimuovi i preventivi dalla cartella (li lascia senza cartella)
            self.db.query(Preventivo).filter(
                Preventivo.cartella_id == cartella_id
            ).update({Preventivo.cartella_id: None})
        
        # Sposta le sottocartelle al livello padre della cartella eliminata
        self.db.query(Cartella).filter(
            Cartella.parent_id == cartella_id
        ).update({Cartella.parent_id: db_cartella.parent_id})
        
        # Elimina la cartella
        self.db.delete(db_cartella)
        self.db.commit()
        
        return True
    
    def sposta_preventivi(self, spostamento: CartellaSpostamento, user_id: str) -> int:
        """
        Sposta uno o più preventivi in una cartella.
        Restituisce il numero di preventivi spostati.
        """
        # Verifica che la cartella di destinazione esista (se specificata)
        if spostamento.cartella_id:
            cartella_destinazione = self.ottieni_cartella(spostamento.cartella_id, user_id)
            if not cartella_destinazione:
                raise ValueError("Cartella di destinazione non trovata")
        
        # Verifica che tutti i preventivi appartengano all'utente
        preventivi_validi = self.db.query(Preventivo).filter(
            Preventivo.id.in_(spostamento.preventivo_ids),
            Preventivo.user_id == user_id
        ).all()
        
        if len(preventivi_validi) != len(spostamento.preventivo_ids):
            raise ValueError("Alcuni preventivi non sono stati trovati o non appartengono all'utente")
        
        # Sposta i preventivi
        num_aggiornati = self.db.query(Preventivo).filter(
            Preventivo.id.in_(spostamento.preventivo_ids),
            Preventivo.user_id == user_id
        ).update(
            {Preventivo.cartella_id: spostamento.cartella_id},
            synchronize_session=False
        )
        
        self.db.commit()
        return num_aggiornati
    
    def ottieni_preventivi_cartella(self, cartella_id: Optional[str], user_id: str, stato_record: str = "attivo") -> List[Preventivo]:
        """
        Ottiene tutti i preventivi di una cartella.
        Se cartella_id è None, ottiene i preventivi senza cartella.
        """
        query = self.db.query(Preventivo).filter(
            Preventivo.user_id == user_id,
            Preventivo.stato_record == stato_record
        )
        
        if cartella_id is None:
            query = query.filter(Preventivo.cartella_id.is_(None))
        else:
            query = query.filter(Preventivo.cartella_id == cartella_id)
        
        return query.order_by(Preventivo.updated_at.desc()).all()
    
    def _crea_ciclo(self, cartella_id: str, nuovo_parent_id: str, user_id: str) -> bool:
        """
        Verifica se impostare nuovo_parent_id come padre di cartella_id creerebbe un ciclo.
        """
        if cartella_id == nuovo_parent_id:
            return True
        
        # Risali nella gerarchia dal nuovo parent per vedere se raggiungiamo cartella_id
        current_id = nuovo_parent_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            if current_id == cartella_id:
                return True
            
            parent = self.db.query(Cartella).filter(
                Cartella.id == current_id,
                Cartella.user_id == user_id
            ).first()
            
            current_id = str(parent.parent_id) if parent and parent.parent_id else None
        
        return False 