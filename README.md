# 🧾 App Preventivi Modulari (LLM-Ready)

Un'applicazione web per la generazione di preventivi con architettura modulare progettata per future integrazioni LLM.

## 📋 Stato Progetto

**Fase Attuale**: Transizione verso Integrazione LLM  
**Ultimo Aggiornamento**: 2024-12-17

✅ **Sistema Base Completato** (Fase 1)  
✅ **Template Unificato PDF/Web** (Ottimizzazione rendering)  
✅ **Migrazione PostgreSQL** (Database produzione)  
✅ **Design Integrazione LLM** (Documento operativo completo)  
🔄 **Prossimo**: Template Documenti Personalizzabili (Fase 2a)

## ✨ Features

- 📊 **Dashboard interattiva** con lista preventivi e filtri
- 📝 **Form preventivi modulari** con validazione in tempo reale
- 🧮 **Calcolo automatico totali** e subtotali
- 👁️ **Anteprima live** del documento durante la compilazione
- 💾 **Sistema di salvataggio** completo con database
- 📱 **UI responsiva** con Tailwind CSS
- ⚡ **Interattività HTMX** per aggiornamenti senza reload
- 🔧 **Architettura LLM-ready** per future integrazioni AI

## 🛠️ Stack Tecnologico

### Frontend
- **HTML5** + **Tailwind CSS** per UI responsiva
- **HTMX** per interattività e aggiornamenti parziali
- **Alpine.js** per micro-interazioni e stato locale
- **Font Awesome** per iconografia

### Backend
- **FastAPI** (Python) per API REST
- **Pydantic** per validazione dati e schemi JSON
- **Jinja2** per templating modulare
- **SQLAlchemy** per ORM database

### Database
- **SQLite** per sviluppo (pronto per PostgreSQL)

## 🚀 Quick Start

### Prerequisiti
- Python 3.11+
- Git

### Installazione

```bash
# Clone del repository
git clone https://github.com/hlessio/app-preventivi-modulari.git
cd app-preventivi-modulari

# Creazione ambiente virtuale
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installazione dipendenze
pip install -r requirements.txt

# Avvio server di sviluppo
uvicorn app.main:app --reload --port 8080
```

### Utilizzo

1. Apri il browser su `http://localhost:8080`
2. Naviga nella **Dashboard** per vedere i preventivi esistenti
3. Clicca **"Nuovo Preventivo"** per creare un preventivo
4. Compila i campi e aggiungi voci al preventivo
5. Usa **"Anteprima"** per vedere il documento in tempo reale
6. **"Salva Bozza"** per persistere il preventivo

## 📁 Struttura Progetto

```
app-preventivi-modulari/
├── app/
│   ├── main.py                 # FastAPI app principale
│   ├── models.py              # Modelli Pydantic
│   ├── database.py            # Configurazione database
│   ├── db_models.py           # Modelli SQLAlchemy
│   ├── schemas/               # Schemi JSON modulari
│   ├── services/              # Logica business
│   └── templates/             # Template Jinja2
│       ├── base.html          # Template base
│       ├── dashboard.html     # Dashboard preventivi
│       ├── preventivo_form.html # Form creazione/modifica
│       └── preventivo/        # Template modulari documento
├── requirements.txt           # Dipendenze Python
├── context.md                # Documentazione sviluppo
└── README.md                 # Questo file
```

## 🏗️ Architettura Modulare

Il progetto implementa un'architettura **JSON-centrica** dove:

1. **Schemi JSON modulari** definiscono la struttura dati per ogni sezione del preventivo
2. **Form frontend** raccolgono dati conformi agli schemi
3. **Backend API** valida e assembla i JSON modulari in un JSON "master"
4. **Template Jinja2** renderizzano il documento finale

Questa architettura facilita l'integrazione futura di **Large Language Models** per automatizzare la compilazione dei preventivi.

## 🔮 Roadmap

### ✅ Fase 1: MVP Manuale (COMPLETATO)
- [x] Backend API completo
- [x] Frontend HTMX + Alpine.js
- [x] Sistema CRUD preventivi
- [x] Dashboard e form interattivi

### 🚧 Fase 2: Produzione
- [ ] Setup PostgreSQL
- [X] Export PDF con WeasyPrint
- [ ] Sistema autenticazione utenti
- [ ] Deploy produzione

### 🤖 Fase 3: Integrazione LLM
- [ ] API LLM per generazione automatica preventivi
- [ ] Interfaccia linguaggio naturale
- [ ] Prompt engineering ottimizzato

## 🤝 Contribuire

Le contribuzioni sono benvenute! Sentiti libero di:

1. Fare fork del progetto
2. Creare un branch per la feature (`git checkout -b feature/amazing-feature`)
3. Committare le modifiche (`git commit -m 'Add amazing feature'`)
4. Push del branch (`git push origin feature/amazing-feature`)
5. Aprire una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 👨‍💻 Autore

**Alessio** - [@hlessio](https://github.com/hlessio)

---

⭐ **Star questo repository se ti è stato utile!** 

## 📚 Documentazione

### Documenti Principali

- **[`context.md`](context.md)** - Contesto generale del progetto e stato sviluppo
- **[`LLM_INTEGRATION_DESIGN.md`](LLM_INTEGRATION_DESIGN.md)** - Design dettagliato integrazione LLM
- **[`MIGRAZIONE_POSTGRESQL.md`](MIGRAZIONE_POSTGRESQL.md)** - Guida migrazione database
- **[`README_PDF_EXPORT.md`](README_PDF_EXPORT.md)** - Documentazione export PDF

### Struttura Progetto

```
app-preventivi2305/
├── app/                     # Applicazione principale
│   ├── main.py             # FastAPI application
│   ├── db_models.py        # Modelli database SQLAlchemy
│   ├── models.py           # Modelli Pydantic per validazione
│   ├── database.py         # Configurazione database
│   ├── services/           # Logica business
│   │   ├── preventivo_service.py
│   │   ├── pdf_export_service.py
│   │   └── preventivo_calculator.py
│   ├── schemas/            # Schemi JSON modulari
│   │   ├── preventivo_master.schema.json
│   │   ├── intestazione_*.schema.json
│   │   └── ...
│   └── templates/          # Template Jinja2
│       ├── preventivo/
│       │   ├── preventivo_unificato.html
│       │   └── _*.html     # Moduli componenti
│       ├── dashboard.html
│       └── base.html
├── alembic/                # Migrazioni database
├── context.md              # Documento contesto progetto
├── LLM_INTEGRATION_DESIGN.md # Design integrazione LLM
└── requirements.txt        # Dipendenze Python
```

## 🚀 Avvio Rapido

### Prerequisiti
- Python 3.11+
- PostgreSQL 14+
- WeasyPrint dependencies (per PDF export)

### Setup

1. **Clone e Environment**
   ```bash
   git clone <repository>
   cd app-preventivi2305
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate    # Windows
   ```

2. **Dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database**
   ```bash
   # Configura .env con DATABASE_URL PostgreSQL
   alembic upgrade head
   ```

4. **Avvio**
   ```bash
   chmod +x start_server.sh
   ./start_server.sh
   ```

## 🏗️ Architettura

### Sistema Attuale (MVP Completato)
- **Backend**: FastAPI con logica assemblaggio JSON modulare
- **Database**: PostgreSQL con supporto JSONB  
- **Frontend**: HTMX + Alpine.js per interattività real-time
- **Template**: Sistema Jinja2 modulare unificato PDF/Web
- **PDF Export**: WeasyPrint con ottimizzazione A4

### Prossima Evoluzione (Integrazione LLM)
- **Template Personalizzabili**: Composizione drag & drop documenti
- **Moduli Custom**: Creazione moduli tramite LLM  
- **Agente AI**: Assistente contestuale per popolamento dati

## 📋 Funzionalità Attuali

✅ **Gestione Preventivi**
- Creazione/modifica preventivi con form modulari
- Calcolo automatico totali e subtotali
- Anteprima live durante compilazione
- Salvataggio e caricamento preventivi

✅ **Export PDF**
- Generazione PDF ottimizzata per A4
- Layout identico tra anteprima web e PDF
- Margini e typography perfetti per stampa

✅ **Dashboard**
- Lista preventivi con filtri e ricerca
- Stati preventivo (bozza, inviato, accettato, etc.)
- Navigazione intuitiva

## 🔮 Roadmap LLM (Fase 2-3)

### Fase 2a: Template Personalizzabili (4-6 settimane)
- Sistema template documenti componibili
- UI drag & drop per composizione  
- Gestione formati multipli (A4, US Letter, etc.)

### Fase 2b: Integrazione LLM Base (3-4 settimane)  
- Servizio LLM con intent classification
- Popolamento automatico dati da input naturale
- Chat widget per assistenza documento

### Fase 2c: Moduli Custom LLM (4-5 settimane)
- Generazione moduli Jinja2 + JSON Schema via LLM
- Editor moduli con validazione automatica
- Libreria moduli personalizzati utente

### Fase 3: Agente LLM Avanzato (6-8 settimane)
- Context-aware conversation management
- Suggerimenti proattivi composizione template
- Voice input e interazioni avanzate

## 🛠️ Sviluppo

### Testing
```bash
# Test PDF generation
python test_pdf_layout.py

# Test template unificato  
python test_template_unificato.py

# Test confronto layout
python test_confronto_layout.py
```

### Database Migrations
```bash
# Crea nuova migrazione
alembic revision --autogenerate -m "descrizione"

# Applica migrazioni
alembic upgrade head
```

## 📖 Per Saperne di Più

- Leggi [`context.md`](context.md) per il contesto completo del progetto
- Consulta [`LLM_INTEGRATION_DESIGN.md`](LLM_INTEGRATION_DESIGN.md) per i dettagli sull'evoluzione LLM
- Vedi [`MIGRAZIONE_POSTGRESQL.md`](MIGRAZIONE_POSTGRESQL.md) per dettagli tecnici database

---

**Nota**: Questo è un progetto in evoluzione attiva. Consulta regolarmente i documenti di contesto per gli aggiornamenti più recenti. 