# Guida Operativa – Migrazione a PostgreSQL e Setup Produzione (Revisionata)

## 📋 STATUS PROGRESSI MIGRAZIONE

**Ultimo aggiornamento**: 2024-05-24 (Data sessione completamento)

### ✅ COMPLETATO
- [x] **Sezione 3.1**: PostgreSQL installato e avviato (Homebrew)
- [x] **Sezione 3.2**: File .env configurato con DATABASE_URL PostgreSQL
- [x] **Sezione 4.1**: app/database.py aggiornato con gestione PostgreSQL/SQLite e avvertimenti
- [x] **Sezione 4.2**: app/db_models.py aggiornato con tipi PostgreSQL (UUID, JSONB, lunghezze stringhe)
- [x] **Sezione 4.3**: requirements.txt verificato - tutte le dipendenze presenti
- [x] **Sezione 5**: Alembic inizializzato e configurato
- [x] **Sezione 5**: alembic.ini configurato (sqlalchemy.url commentato)
- [x] **Sezione 5**: alembic/env.py configurato con caricamento .env e import modelli
- [x] **Sezione 5**: Prima migrazione Alembic creata (`17e5f4072d6d_crea_schema_iniziale_per_postgresql.py`)
- [x] **Sezione 5**: Migrazione applicata con successo (`alembic upgrade head`)
- [x] **Sezione 6**: Database popolato con dati di test (`app.init_db`)
- [x] **Test configurazione**: Verificato che i modelli PostgreSQL funzionino correttamente
- [x] **Test finale**: Database PostgreSQL pienamente funzionante
- [x] **WeasyPrint**: Completamente configurato e funzionante con export PDF

### ✅ MIGRAZIONE COMPLETATA AL 100% + EXPORT PDF RISOLTO

**🎉 LA MIGRAZIONE A POSTGRESQL È STATA COMPLETATA CON SUCCESSO!**

- **Database**: PostgreSQL 14 in esecuzione
- **Utente/DB**: `preventivi_user` / `preventivi_db` creati
- **Tabelle**: `users`, `aziende`, `preventivi` create con tipi nativi PostgreSQL
- **Dati**: Database popolato e testato
- **Performance**: UUID nativi e JSONB implementati
- **Export PDF**: WeasyPrint completamente configurato e funzionante

### 📝 NOTE FINALI
- **PostgreSQL**: Installato tramite Homebrew, configurato e funzionante
- **Alembic**: Sistema di migrazioni pienamente operativo
- **UUID**: Chiavi primarie con UUID nativi PostgreSQL implementate
- **JSONB**: Tipo JSONB per dati preventivi implementato per performance ottimali
- **Configurazione**: Sistema pronto per produzione
- **WeasyPrint**: Dipendenze installate, variabili d'ambiente configurate, endpoint PDF testati e funzionanti

### 🚀 SCRIPT DI AVVIO
- **`start_server.sh`**: Script automatico per avviare l'applicazione con tutte le configurazioni necessarie
- **Uso**: `./start_server.sh` dalla directory root del progetto
- **Funzionalità**: Configura WeasyPrint, attiva venv, verifica dipendenze, avvia server

### ⚠️ NOTA TECNICA
- **WeasyPrint**: Richiede dipendenze di sistema separate per export PDF
- **Database Core**: PostgreSQL pienamente funzionante indipendentemente da WeasyPrint

---

Scopo: fornire istruzioni passo‑passo perché Cursor (e chiunque nel team) possa migrare l'app App Preventivi Modulari da SQLite a PostgreSQL, configurare gli ambienti e mantenere coerenza con Alembic. Questa versione è stata aggiornata per riflettere le best practice relative all'uso dei tipi di dato specifici di PostgreSQL e alla strategia di testing.
1. Prerequisiti
Strumento	Versione minima	Note
Python	 3.11	
PostgreSQL	 14 +	
Docker (opzionale)	20 +	Per PostgreSQL locale e test
psycopg2‑binary	già presente in requirements.txt	Driver Python per PostgreSQL
Alembic	già presente in requirements.txt	Per le migrazioni di schema database
python-dotenv	già presente in requirements.txt	Per la gestione delle variabili d'ambiente
Assicurati di avere un file .env nella directory root del progetto (vedi § 3.2).
2. Panoramica del Database PostgreSQL
Entità	Tabella	Tipi Chiave Postgres	Note
Utenti	users	id: UUID (Primary Key)	Indice su email e username.
Aziende	aziende	id: UUID (Primary Key), user_id: UUID (Foreign Key)	FK → users.id (unique).
Preventivi	preventivi	id: UUID (Primary Key), dati_preventivo: JSONB	FK → users.id.
Tipi di Dato Specifici PostgreSQL:
UUID: Il tipo UUID nativo di PostgreSQL (usato con as_uuid=True in SQLAlchemy) sostituirà String per le chiavi primarie, offrendo migliore performance e unicità globale.
JSONB: Il campo dati_preventivo utilizzerà il tipo JSONB binario di PostgreSQL. Questo permette query efficienti sui dati JSON e la possibilità di creare indici GIN per ricerche avanzate all'interno del JSON.
3. Configurazione dell'Ambiente
3.1. Avviare PostgreSQL Localmente (con Docker)
Per sviluppo e test locali, è consigliato usare Docker:
```bash
docker run --name preventivi-postgres \
  -e POSTGRES_USER=preventivi_user \
  -e POSTGRES_PASSWORD=preventivi_pass \
  -e POSTGRES_DB=preventivi_db \
  -p 5432:5432 -d postgres:14
```
(Nota: utenti e password sono stati resi leggermente più espliciti per chiarezza)
3.2. File .env di Esempio
Crea o aggiorna il file .env nella root del progetto:
```env
# === Database ===
# Per sviluppo e produzione con PostgreSQL:
DATABASE_URL=postgresql+psycopg2://preventivi_user:preventivi_pass@localhost:5432/preventivi_db

# Per testing automatico (configurato per usare un DB PostgreSQL separato, vedi sezione Test):
# TEST_DATABASE_URL=postgresql+psycopg2://test_user:test_pass@localhost:5433/test_preventivi_db

# Opzione per avvio rapido in dev (solo per verifiche minimali, i modelli sono ottimizzati per PG):
# DATABASE_URL=sqlite:///./preventivi_dev_fallback.db
```
NB: Il prefisso `postgresql+psycopg2` è richiesto da SQLAlchemy per usare il driver psycopg2.
4. Aggiornare il Codebase
4.1. app/database.py
Modifica il file per gestire la connessione a PostgreSQL e opzionalmente a SQLite, con la dovuta cautela.
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
4.2. app/db_models.py
Aggiorna i modelli SQLAlchemy per utilizzare i tipi di dato specifici di PostgreSQL.
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON # JSON può rimanere per type hinting generico se serve
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB # Import tipi specifici PG
import uuid # Per il default delle colonne UUID
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    # Usa UUID nativo di PostgreSQL, con default Python per la generazione
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    # ... (altri campi come prima)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    azienda = relationship("Azienda", back_populates="proprietario", uselist=False)
    preventivi = relationship("Preventivo", back_populates="utente")

class Azienda(Base):
    __tablename__ = "aziende"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True) # Anche FK deve essere UUID
    # ... (altri campi come prima, assicurati che i tipi stringa abbiano lunghezze appropriate se necessario)
    nome_azienda = Column(String(255), nullable=False) # Esempio: aggiunta lunghezza
    # ...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    proprietario = relationship("User", back_populates="azienda")

class Preventivo(Base):
    __tablename__ = "preventivi"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Anche FK deve essere UUID
    numero_preventivo = Column(String(100), nullable=False, index=True) # Esempio: aggiunta lunghezza
    oggetto_preventivo = Column(String(500), nullable=False) # Esempio: aggiunta lunghezza
    stato_preventivo = Column(String(50), default="bozza")
    
    # Usa JSONB per performance e capacità di query avanzate su PostgreSQL
    dati_preventivo = Column(JSONB, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    utente = relationship("User", back_populates="preventivi")
```
Nota Importante: Con queste modifiche, i modelli sono ottimizzati per PostgreSQL. L'uso con SQLite (tramite il fallback in DATABASE_URL) potrebbe avere limitazioni o non funzionare correttamente per tutte le feature (es. query JSON avanzate). Tutti i test che interagiscono con il DB dovrebbero essere eseguiti contro PostgreSQL.
4.3. requirements.txt
Verifica che le seguenti dipendenze (già presenti nel tuo requirements.txt originale) siano installate:
```text
python-dotenv
psycopg2-binary
alembic
sqlalchemy
fastapi
uvicorn[standard]
jinja2
weasyprint
```
5. Configurazione e Utilizzo di Alembic
Alembic gestirà le migrazioni dello schema del database.
Inizializzazione (se non già fatta):
Se non hai ancora una directory alembic, esegui:
```bash
alembic init alembic
```
Configurazione alembic.ini:
Modifica alembic.ini per puntare alla variabile d'ambiente DATABASE_URL.
Trova la riga sqlalchemy.url e modificala o assicurati che sia commentata se la gestisci in env.py:
```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
# Oppure, se si usa la lettura da env.py:
# (lasciare commentato o vuoto qui)
```
Configurazione alembic/env.py:
Modifica alembic/env.py per:
Caricare le variabili d'ambiente da .env.
Impostare sqlalchemy.url dinamicamente.
Far conoscere ad Alembic i metadati dei tuoi modelli SQLAlchemy (Base.metadata).
All'inizio di alembic/env.py:
```python
import os
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Importa Base dai tuoi modelli SQLAlchemy
# Assicurati che il path sia corretto per la struttura del tuo progetto
# Ad esempio, se alembic è nella root e l'app è in 'app_folder':
# from app_folder.db_models import Base
# Nel tuo caso, con alembic nella root e i modelli in app/db_models.py:
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))) # Aggiunge la root del progetto a sys.path
from app.db_models import Base # Ora l'import dovrebbe funzionare

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Imposta sqlalchemy.url usando la variabile d'ambiente
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL non è impostata nel file .env o nell'ambiente.")
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aggiungi i metadati del tuo modello qui per il supporto 'autogenerate'
target_metadata = Base.metadata # MODIFICA QUI

# ... resto del file env.py ...
# Assicurati che target_metadata sia usato in run_migrations_offline() e run_migrations_online()
# Esempio per run_migrations_online():
# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.
#     ...
#     """
#     connectable = ...
#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata # ASSICURATI SIA QUI
#         )
#         with context.begin_transaction():
#             context.run_migrations()
```
Assicurati che `target_metadata = Base.metadata` sia referenziato correttamente nelle funzioni `run_migrations_offline` e `run_migrations_online`.
Creare la Prima Migrazione (Autogenerate):
Dopo aver modificato `app/db_models.py` con i tipi PostgreSQL e configurato `alembic/env.py`:
Assicurati che il tuo database PostgreSQL sia in esecuzione e accessibile.
È FONDAMENTALE che il database puntato da DATABASE_URL sia VUOTO o non ancora esistente la prima volta che generi lo schema iniziale, per evitare conflitti.
```bash
alembic revision -m "crea schema iniziale per postgresql" --autogenerate
```
Ispeziona il file di migrazione generato in `alembic/versions/`. Dovrebbe contenere le istruzioni per creare le tabelle `users`, `aziende`, e `preventivi` con i tipi UUID e JSONB.
Applicare la Migrazione:
```bash
alembic upgrade head
```
Questo applicherà la migrazione al tuo database PostgreSQL, creando le tabelle.
Versioning Futuro:
Ogni volta che modifichi `app/db_models.py` (es. aggiungi una colonna, una tabella, un indice):
```bash
alembic revision -m "descrizione della modifica" --autogenerate
alembic upgrade head
```
6. Migrazione dei Dati Esistenti (da SQLite a PostgreSQL)
La guida originale non copriva questo aspetto. Se hai dati importanti nel tuo database SQLite (`preventivi_test.db` o altro) che devono essere trasferiti a PostgreSQL, dovrai pianificare una migrazione dei dati. `init_db.py` popolerà il nuovo DB con dati di esempio, ma non trasferirà dati preesistenti.
Opzioni per la migrazione dei dati:
Script ETL Personalizzato: Scrivi uno script Python che legge da SQLite e scrive su PostgreSQL usando SQLAlchemy.
Strumenti Esterni: Utilizza strumenti come `pgloader` (molto potente e specifico per questo).
Esportazione/Importazione CSV: Esporta i dati da SQLite in CSV e importali in PostgreSQL (può essere complesso per le relazioni e i JSON).
Se `app/init_db.py` è sufficiente per popolare il database con i dati necessari per lo sviluppo/test, puoi saltare questo passaggio. Se lo esegui, aggiornerà il database PostgreSQL puntato da DATABASE_URL.
```bash
# Esempio di esecuzione del seeder (assicurati che DATABASE_URL punti a PostgreSQL)
python -m app.init_db
```
7. Gestione Multi-Ambiente
Utilizza il file `.env` per gestire le configurazioni del database tra diversi ambienti:
Ambiente	DATABASE_URL Esempio	Note
Dev-SQLite Fallback	`sqlite:///./preventivi_dev_fallback.db`	Avvio rapido, nessun servizio esterno. Attenzione: non pienamente compatibile con modelli PG.
Local-PostgreSQL	`postgresql+psycopg2://preventivi_user:preventivi_pass@localhost:5432/preventivi_db`	Consigliato per sviluppo locale (Docker § 3.1).
Test-PostgreSQL	`postgresql+psycopg2://test_user:test_pass@localhost:5433/test_preventivi_db`	DB separato per test automatici (vedi § 9).
Produzione	es. `postgresql+psycopg2://user:pass@prod-db-host:5432/prod_db`	Fornito dal provider cloud, gestito come variabile segreta.
Il codice dovrebbe leggere DATABASE_URL da `.env` senza modifiche dirette ai file Python per cambiare ambiente.
8. Backup e Restore (PostgreSQL CLI con Docker)
Esempio per il container Docker `preventivi-postgres`:
Backup:
```bash
docker exec preventivi-postgres pg_dump -U preventivi_user -Fc preventivi_db > preventivi_backup.dump
```
Restore (assicurati che il database `preventivi_db` esista e sia vuoto o preparato per il restore):
```bash
cat preventivi_backup.dump | docker exec -i preventivi-postgres pg_restore -U preventivi_user -d preventivi_db
```
Oppure, se il dump non è compresso (-Fc), usa `psql`:
```bash
# Per dump SQL plain text
# docker exec -i preventivi-postgres psql -U preventivi_user -d preventivi_db < backup.sql
```
9. Testing
È cruciale testare l'applicazione contro un database PostgreSQL per garantire coerenza con l'ambiente di produzione.
Strategia Consigliata: Utilizza un database PostgreSQL dedicato per i test automatici (es. pytest). Questo può essere un container Docker effimero avviato e fermato dalla tua suite di test o un'istanza separata.
Configurazione:
Definisci una `TEST_DATABASE_URL` nel tuo file `.env` (o gestiscila tramite variabili d'ambiente nel CI).
Nella configurazione dei test (`conftest.py` per pytest), sovrascrivi la dipendenza `get_db` per usare `TEST_DATABASE_URL` e assicurati che le tabelle vengano create (e possibilmente droppate) prima/dopo ogni sessione o test.
Esempio (`conftest.py` per pytest):
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

from app.main import app # La tua app FastAPI
from app.database import Base, get_db # get_db originale
# from app.db_models import * # Assicurati che i modelli siano importati da Base

load_dotenv()

# Usa un URL di database PostgreSQL per i test
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://test_user:test_pass@localhost:5433/test_preventivi_db")
if not TEST_DATABASE_URL.startswith("postgresql"):
    raise ValueError("TEST_DATABASE_URL deve puntare a un database PostgreSQL per test affidabili.")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea le tabelle nel database di test prima che i test inizino
# e le droppa dopo che sono finiti
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine) # Crea tutte le tabelle
    yield
    Base.metadata.drop_all(bind=engine) # Pulisce dopo i test

# Fixture per sovrascrivere la dipendenza get_db nei test
@pytest.fixture(scope="function")
def db_session_override():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session # Forinisce la sessione al test
    
    session.close()
    transaction.rollback() # Rollback per isolare i test
    connection.close()

@pytest.fixture(scope="function")
def client(db_session_override):
    # Sovrascrivi la dipendenza get_db
    def override_get_db():
        try:
            yield db_session_override
        finally:
            pass # La sessione è già gestita dalla fixture db_session_override

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Rimuovi l'override dopo il test per pulizia
    del app.dependency_overrides[get_db]
```
Questo setup utilizza una sessione e una transazione per test, facendo rollback dopo ogni test per mantenere l'isolamento. Le tabelle sono create una volta per sessione di test.
CI/CD: Configura la tua pipeline CI/CD per avviare un servizio PostgreSQL (es. Docker) prima di eseguire i test.
10. Deploy su Piattaforme Cloud (es. Railway, Render, Heroku, Supabase)
Provisioning Database: Crea un'istanza PostgreSQL gestita sulla tua piattaforma cloud scelta. Ottieni l'URL di connessione del database.
Variabili d'Ambiente: Imposta la variabile d'ambiente `DATABASE_URL` (e altre necessarie come `SECRET_KEY`, ecc.) nel pannello "Secrets" o "Environment Variables" della tua applicazione sulla piattaforma cloud. Non committare mai credenziali nel repository.
Migrazioni: Configura la tua pipeline di deploy (es. GitHub Actions, script di release della piattaforma) per eseguire `alembic upgrade head` come parte del processo di deploy, prima che la nuova versione dell'applicazione venga avviata. Questo assicura che lo schema del database sia aggiornato.
Processo di Avvio: Assicurati che il comando di avvio della tua applicazione (es. `uvicorn app.main:app --host 0.0.0.0 --port $PORT`) sia corretto per la piattaforma.
11. Considerazioni Avanzate per Produzione (Passi Futuri)
Indici su JSONB: Per query performanti sui campi interni della colonna `dati_preventivo` (di tipo JSONB), considera l'aggiunta di indici GIN. Puoi farlo tramite una nuova migrazione Alembic.
Esempio di come potresti definire l'indice nel modello (o aggiungerlo con Alembic):
```python
# In db_models.py, per la colonna dati_preventivo
# from sqlalchemy import Index
# ...
# class Preventivo(Base):
#   ...
#   dati_preventivo = Column(JSONB, nullable=False)
#   ...
#   __table_args__ = (
#       Index('ix_preventivi_dati_preventivo_gin', dati_preventivo, postgresql_using='gin'),
#   )
```
Connection Pooling: SQLAlchemy usa un pool di connessioni di default (QueuePool). Per applicazioni ad alto traffico, potresti aver bisogno di ottimizzare i parametri del pool (es. `pool_size`, `max_overflow`, `pool_timeout`) in `create_engine`.
Sicurezza: Segui le best practice per la sicurezza del database, inclusa la gestione delle credenziali, accessi di rete limitati, e aggiornamenti regolari.
Monitoring e Logging: Implementa un adeguato monitoring delle performance del database e logging per l'applicazione.
12. Checklist Finale per la Migrazione
File `.env` configurato correttamente con `DATABASE_URL` che punta a PostgreSQL.
Istanza PostgreSQL (locale via Docker o remota) attiva e accessibile.
Modelli SQLAlchemy (`app/db_models.py`) aggiornati con tipi UUID e JSONB.
`alembic/env.py` configurato per caricare `.env` e usare `Base.metadata`.
Prima migrazione Alembic generata (`--autogenerate`) su un DB PostgreSQL vuoto.
`alembic upgrade head` eseguito con successo sul DB PostgreSQL.
(Opzionale) Dati esistenti migrati da SQLite a PostgreSQL, se necessario.
(Opzionale) `app/init_db.py` eseguito per popolare il DB PostgreSQL con dati di seed.
Applicazione avviata (`uvicorn app.main:app ...`) si connette correttamente a PostgreSQL.
Funzionalità CRUD base (es. creare, leggere, salvare un preventivo) testate manualmente sull'applicazione connessa a PostgreSQL.
Suite di test automatici configurata per girare contro un DB PostgreSQL di test ed eseguita con successo.
Piano di backup per il database di produzione definito.
Se tutti i punti applicabili sono verificati, la migrazione a PostgreSQL è completata e l'applicazione è pronta per un ambiente basato su PostgreSQL. 