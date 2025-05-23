#!/usr/bin/env python3
"""
Script di inizializzazione del database.
Crea le tabelle e inserisce alcuni dati di esempio.
"""
import uuid
from datetime import datetime, date
from .database import SessionLocal, engine
from .db_models import Base, User, Azienda, Preventivo

def init_db():
    """Inizializza il database con le tabelle e dati di esempio"""
    
    # Crea tutte le tabelle
    Base.metadata.create_all(bind=engine)
    
    # Crea una sessione
    db = SessionLocal()
    
    try:
        # Controlla se esistono già dei dati
        existing_user = db.query(User).first()
        if existing_user:
            print("Database già inizializzato.")
            return
        
        # Crea un utente di esempio
        user_id = str(uuid.uuid4()) # Convertiamo in stringa
        user = User(
            id=user_id,
            email="admin@example.com",
            username="admin",
            hashed_password="fake_hashed_password",  # In un'app reale questo sarebbe un hash
            is_active="active"
        )
        db.add(user)
        
        # Crea un'azienda di esempio
        azienda = Azienda(
            user_id=user_id,
            nome_azienda="Azienda di Esempio S.r.l.",
            logo_url="https://example.com/logo.png",
            partita_iva_azienda="12345678901",
            codice_fiscale_azienda="ABCDEF12G34H567I",
            indirizzo_via="Via Roma, 123",
            indirizzo_cap="00100",
            indirizzo_citta="Roma",
            indirizzo_provincia="RM",
            indirizzo_nazione="Italia",
            email_azienda="info@aziendaesempio.it",
            telefono_azienda="+39 06 1234567",
            sito_web_azienda="https://www.aziendaesempio.it"
        )
        db.add(azienda)
        
        # Crea un preventivo di esempio
        preventivo_data = {
            "metadati_preventivo": {
                "id_preventivo": str(uuid.uuid4()),
                "numero_preventivo": "2024/001",
                "data_emissione": "2024-01-15",
                "data_scadenza": "2024-02-15",
                "oggetto_preventivo": "Sviluppo sito web aziendale",
                "stato_preventivo": "bozza"
            },
            "azienda_emittente": {
                "nome_azienda": "Azienda di Esempio S.r.l.",
                "logo_url": "https://example.com/logo.png",
                "partita_iva_azienda": "12345678901",
                "codice_fiscale_azienda": "ABCDEF12G34H567I",
                "indirizzo_azienda": {
                    "via": "Via Roma, 123",
                    "cap": "00100",
                    "citta": "Roma",
                    "provincia": "RM",
                    "nazione": "Italia"
                },
                "email_azienda": "info@aziendaesempio.it",
                "telefono_azienda": "+39 06 1234567",
                "sito_web_azienda": "https://www.aziendaesempio.it"
            },
            "cliente_destinatario": {
                "nome_cliente": "Cliente di Prova S.r.l.",
                "partita_iva": "98765432109",
                "indirizzo": {
                    "via": "Via Milano, 456",
                    "cap": "20100",
                    "citta": "Milano",
                    "provincia": "MI",
                    "nazione": "Italia"
                },
                "email": "contatti@clienteprova.it",
                "telefono": "+39 02 9876543",
                "referente": "Mario Rossi"
            },
            "corpo_preventivo": {
                "righe": [
                    {
                        "descrizione": "Progettazione UX/UI",
                        "quantita": 40,
                        "unita_misura": "ore",
                        "prezzo_unitario_netto": 80.0,
                        "percentuale_iva": 22
                    },
                    {
                        "descrizione": "Sviluppo frontend",
                        "quantita": 60,
                        "unita_misura": "ore",
                        "prezzo_unitario_netto": 75.0,
                        "percentuale_iva": 22
                    },
                    {
                        "descrizione": "Sviluppo backend",
                        "quantita": 80,
                        "unita_misura": "ore",
                        "prezzo_unitario_netto": 85.0,
                        "percentuale_iva": 22
                    }
                ],
                "note_tabella": "Tutti i lavori saranno completati entro 2 mesi dalla data di inizio."
            },
            "condizioni_contrattuali": {
                "testo_condizioni": "Pagamento: 50% all'ordine, 50% alla consegna. Validità offerta: 30 giorni."
            },
            "dettagli_totali": {
                "totale_imponibile_netto": 0.0,  # Verrà calcolato automaticamente
                "totale_iva": 0.0,
                "totale_generale_lordo": 0.0
            },
            "elementi_footer": {
                "dati_pagamento": "IBAN: IT60 X054 2811 1010 0000 0123 456",
                "validita_preventivo": "30 giorni dalla data di emissione",
                "note_finali": "Grazie per averci scelto!",
                "firma_azienda": "Il Team di Azienda di Esempio"
            }
        }
        
        preventivo = Preventivo(
            user_id=user_id,
            numero_preventivo="2024/001",
            oggetto_preventivo="Sviluppo sito web aziendale",
            stato_preventivo="bozza",
            dati_preventivo=preventivo_data
        )
        db.add(preventivo)
        
        # Commit di tutti i dati
        db.commit()
        
        print("Database inizializzato con successo!")
        print(f"User ID: {user_id}")
        print(f"Preventivo ID: {preventivo.id}")
        
    except Exception as e:
        print(f"Errore durante l'inizializzazione del database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 