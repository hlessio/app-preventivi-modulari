# 🧾 App Preventivi Modulari (LLM-Ready)

Un'applicazione web per la generazione di preventivi con architettura modulare progettata per future integrazioni LLM.

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