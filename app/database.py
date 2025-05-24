from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# URL del database: priorità a PostgreSQL.
# Il fallback a SQLite è solo per comodità in DEV se Docker non è attivo,
# ma ricorda che i modelli (db_models.py) sono ottimizzati per PostgreSQL
# e i test dovrebbero sempre girare su PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./preventivi_dev_fallback.db")

connect_args = {}
# Argomenti specifici per SQLite
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    print("ATTENZIONE: Connessione a SQLite. I modelli sono ottimizzati per PostgreSQL.")
    print("           Questa modalità è per sviluppo rapido, non per testing completo o produzione.")

# `echo=False` è consigliato per produzione, True per debug SQL in dev.
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# Configurazione della sessione
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli
Base = declarative_base()

# Dependency per ottenere la sessione del database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 