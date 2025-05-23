from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# URL del database - per i test usiamo SQLite
# DATABASE_URL = os.getenv(
#     "DATABASE_URL", 
#     "postgresql://postgres:password@localhost:5432/preventivi_db"
# )

# Per i test, usiamo SQLite temporaneamente
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./preventivi_test.db"
)

# Creazione del motore SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

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