# CONTESTO DI SVILUPPO PER L'AGENT AI (CURSOR) - Applicazione Generazione Documenti Modulari

**Obiettivo del Progetto:**
Sviluppare un'applicazione web per la generazione di documenti (inizialmente preventivi) attraverso un sistema di templating modulare (Jinja2) e un'interfaccia utente interattiva (HTMX + Alpine.js). L'architettura è "LLM-ready", progettata per una futura integrazione "plug and play" di Large Language Models per automatizzare l'inserimento dati.

**Architettura Chiave (MVP Manuale, LLM-Ready):**
1.  **Frontend:** HTML, HTMX, Alpine.js per form di input modulari e anteprima dinamica.
2.  **Backend (Python/FastAPI):**
    *   API per gestire operazioni sui documenti e sui loro moduli.
    *   Logica di **Assemblaggio JSON**: Riceve dati dai form (strutturati secondo schemi JSON modulari), li assembla in un **JSON "master"** per il documento.
    *   **Motore di Templating (Jinja2):** Renderizza i template HTML dei moduli usando il JSON "master".
3.  **Database (PostgreSQL):** Memorizza utenti, dati aziendali, definizioni dei moduli (inclusi i loro **schemi JSON di input**), e documenti salvati (come JSON "master").
4.  **JSON come "Contratto":**
    *   Ogni modulo HTML (es. `intestazione-cliente.html`, `tabella-preventivo.html`) ha uno schema JSON di input ben definito (es. `intestazione-cliente.schema.json`).
    *   L'input utente (manuale nell'MVP) o l'output LLM (futuro) deve conformarsi a questi schemi JSON modulari.
    *   Questi JSON modulari vengono aggregati dal backend in un JSON "master" che rappresenta l'intero documento.
    *   Questo JSON master è l'unico input per il rendering del template Jinja2 principale.

**Fasi di Sviluppo (vedi Documento di Sviluppo v1.1 per dettagli):**
*   **Fase 0:** Progettazione Dettagliata Schemi e Moduli (LLM-Ready) - **COMPLETATA** (Setup ambiente base incluso)
*   **Fase 1:** MVP - Preventivatore Manuale Modulare (LLM-Ready) - **COMPLETATA AL 100%**
    *   [X] Backend: API base, logica assemblaggio JSON, rendering Jinja2. (Endpoint di visualizzazione base implementato)
    *   [X] Backend: Validazione input con Pydantic. (Modelli Pydantic creati in `app/models.py` e integrati nell'endpoint `/preventivo/visualizza`)
    *   [X] Backend: Logica di calcolo per totali e subtotali. (Implementato in `app/services/preventivo_calculator.py`)
    *   [X] Database: Schemi DB, modelli per utenti, moduli, documenti. (SQLAlchemy + SQLite funzionante, servizio CRUD completo)
    *   [X] Frontend: Form input per moduli chiave, interattività tabella preventivo con HTMX. (Layout form preventivi con sidebar e anteprima full-page implementato)
    *   [X] Moduli Chiave Preventivo: `intestazione-azienda`, `intestazione-cliente`, `tabella-preventivo`, `condizioni-generali`, `footer-preventivo`. (Schemi e template HTML/Jinja2 completamente funzionanti)
    *   [X] Schemi JSON per Moduli Chiave: Definiti e pronti per essere usati. (Completato in Fase 0, integrati in Pydantic)
*   **Fase 2:** Integrazione LLM - Livello 1 (Automazione Input) - *Futura*
*   **Fase 3:** Funzionalità LLM Avanzate - *Futura*

---
**STATO ATTUALE DELLO SVILUPPO (Aggiornare regolarmente):**
*   **Data Ultimo Aggiornamento:** 2024-12-17 (Template Unificato Completato)
*   **Fase Corrente:** Fase 2 - Produzione
*   **Step Attuale:** ✅ **Template Unificato PDF/Web Completato** + 🔄 **Migrazione PostgreSQL in corso**
    *   ✅ **Backend core per preventivi pienamente funzionante** (dalla Fase 1)
    *   ✅ Modelli Pydantic completi (`app/models.py`) integrati e funzionanti (dalla Fase 1)
    *   ✅ Logica di calcolo totali/subtotali implementata (`app/services/preventivo_calculator.py`) (dalla Fase 1)
    *   ✅ Template Jinja2 completamente funzionanti con numerazione righe corretta (dalla Fase 1)
    *   ✅ Sistema di rendering HTML completo e testato (sia da POST che da DB) (dalla Fase 1)
    *   ✅ Servizio preventivi con CRUD operations completo (`app/services/preventivo_service.py`) (dalla Fase 1)
    *   ✅ **Frontend completo implementato** (dalla Fase 1):\
        *   ✅ Dashboard interattiva con lista preventivi, filtri e ricerca
        *   ✅ **Layout pagina creazione/modifica preventivo con sidebar per form e area documento full-page per anteprima live (UX migliorata)**
        *   ✅ Form preventivi modulari con HTMX per interattività in tempo reale (campi indirizzo cliente separati)
        *   ✅ Tabella voci preventivo (ora lista voci compatta nella sidebar) completamente interattiva (aggiungi/rimuovi/modifica)
        *   ✅ Calcolo automatico totali in tempo reale
        *   ✅ Anteprima live del documento durante la compilazione
        *   ✅ **Sistema di salvataggio funzionante e robusto** (fix problemi tasto "salva bozza", validazione Pydantic indirizzi, serializzazione UUID)
        *   ✅ Navigazione tra pagine completa
        *   ✅ UI responsiva con Tailwind CSS
        *   ✅ Sistema notifiche utente implementato
        *   ✅ Debugging e risoluzione problemi interattività completato
    *   ✅ **NUOVO: Sistema Template Unificato PDF/Web COMPLETATO**
        *   ✅ **Problema Risolto**: Eliminato dual template system (`preventivo_documento.html` vs `preventivo_pdf.html`)
        *   ✅ **Template Unificato**: Creato `preventivo_unificato.html` con CSS media queries (@media screen vs @media print)
        *   ✅ **Identità Garantita**: Layout identico tra anteprima web e PDF generato
        *   ✅ **Ottimizzazione A4**: Margini perfetti (1.2cm x 0.8cm), layout a 21cm per web, dimensioni font ottimizzate
        *   ✅ **CSS Integrato**: Tutto il CSS incorporato nel template, eliminazione CSS service conflicts
        *   ✅ **Servizio PDF Aggiornato**: `PDFExportService` refactored per usare template unificato
        *   ✅ **Endpoint Unificati**: Entrambi `/preventivo/visualizza` e `/preventivo/pdf` usano stesso template
        *   ✅ **Testing Completo**: Scripts `test_template_unificato.py`, `test_pdf_layout.py`, `test_confronto_layout.py`
        *   ✅ **Risoluzione Issues**: Fix CSS type hints, Jinja2 filter `strftime`, WeasyPrint configuration
        *   ✅ **Performance**: PDF ~22-25KB, no content overflow, perfect A4 compliance
    *   ✅ **Export PDF con WeasyPrint completato e ottimizzato**
        *   ✅ Servizio `PDFExportService` implementato e refactored (`app/services/pdf_export_service.py`)
        *   ✅ ~~Template HTML dedicato `preventivo_pdf.html` con CSS ottimizzato per A4~~ → **Sostituito con template unificato**
        *   ✅ Endpoint API: `POST /preventivo/pdf` e `GET /preventivo/{id}/pdf`
        *   ✅ Integrazione UI nella dashboard e nel form preventivo per scaricare PDF
        *   ✅ Script di test `test_pdf.py` e `quick_pdf_test.py` creati e funzionanti
        *   ✅ Documentazione `README_PDF_EXPORT.md` creata
        *   ✅ **WeasyPrint completamente configurato**: Dipendenze sistema installate, variabili d'ambiente configurate
        *   ✅ **Script di avvio `start_server.sh`**: Automatizza configurazione WeasyPrint e avvio server
        *   ✅ **Test endpoint funzionanti**: PDF generati correttamente con template unificato
    *   🔄 **Migrazione a PostgreSQL (in corso)**
        *   ✅ **Configurazione Ambiente**: File `.env` configurato con DATABASE_URL PostgreSQL
        *   ✅ **Database Layer**: `app/database.py` aggiornato per PostgreSQL con fallback SQLite e avvertimenti
        *   ✅ **Modelli Dati**: `app/db_models.py` aggiornato con tipi PostgreSQL nativi (UUID, JSONB, lunghezze stringhe)
        *   ✅ **Dipendenze**: `requirements.txt` verificato - tutte le dipendenze PostgreSQL presenti
        *   ✅ **Migrations Setup**: Alembic inizializzato e configurato (`alembic.ini`, `alembic/env.py`)
        *   ✅ **Configurazione Test**: Verificato che modelli PostgreSQL non siano compatibili con SQLite (comportamento atteso)
        *   ✅ **Documentazione**: Creata guida completa `MIGRAZIONE_POSTGRESQL.md` con status tracking
        *   ⏳ **In Attesa**: Istanza PostgreSQL in esecuzione (Docker non installato, richiede setup manuale/cloud)
        *   ⏳ **Prossimi Step**: Prima migrazione Alembic, test con database PostgreSQL reale
*   **Repository e Documentazione**:\
        *   ✅ Versioning Git inizializzato e configurato
        *   ✅ Documentazione completa migrazione PostgreSQL
*   **Prossimi Passi Immediati - Fase 2: Produzione:**
    1.  ✅ **Export PDF**: Integrazione WeasyPrint per generazione PDF - **COMPLETATO**
    2.  ✅ **NUOVO: Template Unificato PDF/Web** - **COMPLETATO**
        *   ✅ Risolto dual template system 
        *   ✅ Layout identico tra web e PDF garantito
        *   ✅ Ottimizzazione A4 perfetta
        *   ✅ Sistema di testing completo
    3.  🔄 **Database Produzione**: Migrazione da SQLite a PostgreSQL - **IN CORSO (80% completato)**
        *   ✅ Configurazione codebase e Alembic
        *   ⏳ Setup istanza PostgreSQL e prima migrazione
    4.  **Sistema Autenticazione**: Login/registrazione utenti reali (sostituire test-user)
    5.  **Deploy Cloud**: Setup Heroku/Railway/DigitalOcean per hosting
    6.  **Testing**: Suite test automatizzati (pytest)
    7.  **CI/CD**: Pipeline GitHub Actions per deploy automatico
*   **Bloccanti / Domande Aperte:**
    *   **PostgreSQL Setup**: Docker non installato, necessario setup PostgreSQL manuale o servizio cloud
    *   **Configurazione pronta**: Tutto il codice è pronto per PostgreSQL, serve solo istanza DB attiva

---
**Istruzioni per l'Agent AI (Cursor):**
*   Questo documento serve come **fonte primaria di verità** per il contesto del progetto.
*   Mentre mi assisti nello sviluppo del codice, sentiti libero di **fare riferimento a questo contesto** per comprendere gli obiettivi e l'architettura.
*   Se implementiamo una nuova funzionalità o completiamo uno step, per favore **ricordami di aggiornare la sezione "STATO ATTUALE DELLO SVILUPPO"** o, se hai la capacità, **proponi direttamente un aggiornamento** a questa sezione.
*   Se il codice che stiamo scrivendo o le decisioni che stiamo prendendo sembrano deviare significativamente dall'architettura o dagli obiettivi qui descritti, per favore segnalamelo.
*   Il tuo contributo nel mantenere questo contesto aggiornato è prezioso!

**Parole Chiave per Ricerca Veloce:** `Architettura JSON`, `JSON Master`, `JSON Modulare`, `HTMX`, `Jinja2`, `MVP Manuale`, `LLM-Ready`, `Sidebar Layout`.
---

**Come Usarlo con Cursor:**

1.  **Salva questo testo:** Puoi metterlo all'inizio del tuo file Python principale (es. `main.py`) come un lungo commento, oppure in un file `PROJECT_CONTEXT.md` nella root del tuo progetto. Se Cursor ha una feature per "caricare contesto" da file specifici, usa quella.
2.  **Riferimento Iniziale:** Quando inizi una sessione di chat con l'agent di Cursor, potresti dire qualcosa come: "Sto lavorando al progetto descritto nel file `PROJECT_CONTEXT.md` (o all'inizio di `main.py`). Puoi prenderlo come riferimento principale? Attualmente siamo [descrivi brevemente lo step attuale]."
3.  **Aggiornamenti:** Dopo aver completato una parte significativa, chiedi all'agent: "Abbiamo appena completato [descrizione task]. Puoi aiutarmi ad aggiornare la sezione 'STATO ATTUALE DELLO SVILUPPO' nel nostro documento di contesto?" o fallo direttamente tu.

Questo documento dettaglia lo sviluppo di un'applicazione web per la generazione di documenti modulari, con un focus iniziale sulla creazione di un sistema manuale pienamente funzionante (MVP). L'architettura di questo MVP, in particolare la gestione dei dati tramite JSON modulari e il rendering tramite template Jinja2, è specificamente progettata per consentire una successiva integrazione "plug and play" di Large Language Models (LLM) per automatizzare l'inserimento dati e offrire funzionalità avanzate. L'obiettivo primario dell'MVP è la gestione di preventivi.
Indice:
Introduzione e Scopo del Progetto (con Enfasi MVP)
Visione del Prodotto e Flusso Utente (Distinzione tra MVP Manuale e Visione Finale LLM)
Architettura del Sistema (Dettaglio Architettura MVP e come si adatta alla Visione Finale)
Requisiti Funzionali Chiave (Focus MVP)
Requisiti Non Funzionali Chiave
Stack Tecnologico Proposto
Fasi di Sviluppo e Roadmap Dettagliata
Fase 0: Progettazione Dettagliata Schemi e Moduli (LLM-Ready)
Fase 1: MVP - Preventivatore Manuale Modulare (LLM-Ready)
Fase 2: Integrazione LLM - Livello 1 (Automazione Input tramite LLM)
Fase 3: Funzionalità LLM Avanzate e Rifinitura Continua
Modello Dati e Struttura JSON (Cruciale per LLM-Readiness)
Considerazioni per l'Integrazione LLM Futura
1. Introduzione e Scopo del Progetto (con Enfasi MVP)
Logica del Funzionamento (2 frasi):
L'applicazione, nella sua fase MVP, fornirà un sistema efficiente per creare manualmente preventivi componendoli da moduli predefiniti e inserendo dati in form strutturati. Questa struttura è la base per una futura integrazione LLM che automatizzerà la compilazione basandosi sugli stessi schemi dati.
Dettagli Tecnici:
Il progetto mira a sviluppare un'applicazione web per la generazione di preventivi. L'MVP si concentrerà sulla creazione manuale di questi documenti attraverso un'interfaccia utente interattiva (HTMX + Alpine.js). Gli utenti compileranno sezioni (moduli) del preventivo (es. dati cliente, voci, condizioni). Ogni modulo corrisponde a una porzione di uno schema JSON ben definito. Questi JSON "modulari" vengono aggregati in un JSON "master" che popola i template Jinja2 per il rendering. Questa architettura "JSON-centrica" e modulare è intenzionalmente progettata per facilitare una futura integrazione "plug and play" degli LLM, dove l'LLM genererà i JSON modulari al posto dell'input manuale.
2. Visione del Prodotto e Flusso Utente
Flusso Utente MVP (Manuale):
Selezione/Creazione Preventivo: L'utente inizia un nuovo preventivo.
Composizione (Implicita o Esplicita Semplice): Il sistema presenta una struttura di preventivo predefinita composta da moduli standard (es. intestazione-azienda, intestazione-cliente, tabella-preventivo, condizioni-generali).
Input Dati Modulari: L'utente compila form strutturati per ogni modulo:
Inserisce i dati del cliente nella sezione "Dati Cliente".
Aggiunge/modifica/elimina voci nella "Tabella Preventivo" interattiva.
Seleziona/modifica le "Condizioni Generali".
I dati aziendali sono prelevati dal profilo utente.
Aggiornamento JSON Interno: Ogni input utente aggiorna la porzione corrispondente del JSON "master" del preventivo (o i JSON modulari che poi lo compongono).
Anteprima Live/Rendering (HTMX): Modifiche parziali (es. aggiunta voce) aggiornano dinamicamente l'anteprima del preventivo.
Salvataggio: L'utente salva il preventivo (il JSON master viene persistito).
Esportazione: L'utente esporta il preventivo in PDF.
Logica del Funzionamento (Visione Finale LLM - 2 frasi):
L'utente fornirà input in linguaggio naturale; l'LLM interpreterà questo input e genererà i JSON modulari necessari. Il resto del sistema (assemblaggio JSON, rendering, interazione frontend) funzionerà in modo identico all'MVP manuale.
Flusso Utente (Visione Finale con LLM - Sintesi):
Input Utente (Linguaggio Naturale).
LLM genera i JSON per ciascun modulo rilevante.
Il resto del flusso (assemblaggio JSON, rendering, anteprima, modifica fine, export) è identico all'MVP, ma con i JSON iniziali forniti dall'LLM invece che dall'utente.
3. Architettura del Sistema
Architettura MVP (Manuale, LLM-Ready):
Frontend: HTML, CSS, JavaScript (HTMX per interattività e aggiornamenti parziali, Alpine.js per micro-interazioni). Pagine per la gestione dei preventivi, form strutturati per l'input dati modulare.
Backend API (Python/FastAPI):
Endpoint per gestire le operazioni CRUD sui preventivi e sui loro componenti modulari (es. aggiungere/modificare una voce).
Logica di Assemblaggio JSON: Cruciale. Riceve input dai form (che corrispondono a schemi JSON modulari), li valida (opzionale ma raccomandato), e li assembla in un JSON "master" per il preventivo.
Motore di Templating (Jinja2): Renderizza i template HTML dei moduli e il template principale del documento usando il JSON "master".
Servizio di esportazione PDF.
Database (PostgreSQL): Memorizza utenti, dati aziendali, definizioni dei moduli (nome, path template, schema JSON atteso), e i preventivi salvati (come JSON "master").
JSON come "Contratto": Gli schemi JSON dei moduli sono il "contratto" tra il frontend (form di input), il backend (logica di validazione e assemblaggio), e i template Jinja2. Questo stesso contratto sarà utilizzato dagli LLM.
Logica del Funzionamento (Architettura Futura con LLM - 2 frasi):
L'architettura MVP rimane sostanzialmente invariata. Viene aggiunto un "Servizio LLM" che si interfaccia con le API LLM, riceve l'input utente in linguaggio naturale, e produce i JSON modulari che il backend già sa come processare.
Evoluzione Architetturale per l'LLM:
Servizio LLM: Un nuovo componente/modulo nel backend che:
Contiene la logica per i prompt engineering.
Comunica con le API LLM esterne.
Prende l'output dell'LLM (idealmente già JSON modulari o testo da convertire in essi) e lo passa alla logica di assemblaggio JSON esistente.
Gli endpoint API esistenti potrebbero essere riutilizzati o estesi per accettare input elaborati dall'LLM.
4. Requisiti Funzionali Chiave (Focus MVP)
Logica del Funzionamento (2 frasi):
L'MVP deve consentire la creazione completa e la gestione di preventivi attraverso un'interfaccia manuale intuitiva. La modularità e la gestione dei dati devono essere pronte per l'LLM.
Dettagli Tecnici (MVP):
Gestione Utenti Semplice: Registrazione, login, gestione profilo con dati aziendali (nome, logo, P.IVA, indirizzo, condizioni standard predefinite).
Definizione Moduli (Backend/Configurazione Iniziale):
Definizione dei template HTML/Jinja2 per i moduli chiave del preventivo: intestazione-azienda.html, intestazione-cliente.html, tabella-preventivo.html (con righe interattive), condizioni-generali.html, footer-preventivo.html.
Per ogni modulo, definizione del suo schema JSON di input (questo è fondamentale per la futura integrazione LLM).
Creazione/Modifica Preventivi (Manuale):
Form strutturati nel frontend per inserire/modificare dati per:
Dati Cliente (mappati a intestazione-cliente.json_schema).
Voci del Preventivo (aggiunta, modifica, rimozione interattiva, mappate a tabella-preventivo.json_schema). Ogni voce avrà campi come descrizione, quantità, prezzo unitario, IVA.
Note e selezione/modifica delle Condizioni Generali (mappate ai rispettivi schemi).
I dati dell'azienda sono automaticamente inclusi da intestazione-azienda.html usando i dati del profilo.
Assemblaggio JSON e Rendering: Il backend assembla i dati inseriti nei vari form (validandoli rispetto agli schemi JSON modulari) in un JSON "master". Questo JSON master popola i template Jinja2 per generare l'HTML del preventivo.
Anteprima Dinamica (HTMX): Aggiornamenti in tempo reale di sezioni del preventivo (es. tabella voci, totali) a seguito di input utente, senza ricaricare l'intera pagina.
Calcolo Automatico: Calcolo di subtotali per riga, imponibile totale, IVA totale, totale generale.
Salvataggio Preventivi: Persistenza del JSON "master" del preventivo nel database.
Caricamento Preventivi: Possibilità di ricaricare e modificare preventivi salvati.
Esportazione PDF: Generazione di un PDF del preventivo finale.
5. Requisiti Non Funzionali Chiave
(Come nel documento precedente: Performance, Usabilità, Affidabilità, Manutenibilità, Scalabilità (pensando al futuro LLM), Sicurezza).
Enfasi MVP: Particolare attenzione all'usabilità dell'interfaccia di inserimento manuale e alla reattività garantita da HTMX. La correttezza del ciclo "Input Manuale -> JSON Modulare -> JSON Master -> Rendering" è critica.
6. Stack Tecnologico Proposto
(Come nel documento precedente: Frontend: HTML, CSS, JS, HTMX, Alpine.js. Backend: Python/FastAPI. DB: PostgreSQL. Templating: Jinja2. PDF: WeasyPrint). Nessuna modifica necessaria per l'MVP.
7. Fasi di Sviluppo e Roadmap Dettagliata
Logica Generale delle Fasi (2 frasi):
Si parte dalla definizione precisa degli schemi JSON e dei moduli. Segue lo sviluppo dell'MVP manuale completamente funzionante, che già implementa l'architettura dati per l'LLM. Solo successivamente si integra l'LLM.
**Fase 0: Progettazione Dettagliata Schemi e Moduli (LLM-Ready)**
*   **Obiettivo:** Definire con precisione gli schemi JSON per ogni modulo del preventivo e i relativi template HTML/Jinja2.
*   **Logica del Funzionamento (2 frasi):** Questa fase è la spina dorsale dell'approccio "LLM-ready". Schemi chiari e ben definiti sono essenziali sia per l'input manuale guidato sia per il futuro training/prompting dell'LLM.
*   **Dettagli Tecnici / Attività:**
    1.  **Identificazione Moduli Preventivo:** Confermare i moduli: `intestazione-azienda`, `intestazione-cliente`, `tabella-preventivo` (e `riga_preventivo` come sottomodulo/template), `condizioni-generali`, `footer-preventivo`, `sezione-totali`. - **COMPLETATA**
    2.  **Definizione Schemi JSON Modulari:** Per ogni modulo, creare uno schema JSON che ne definisca la struttura dati attesa (es. usando JSON Schema). *Esempio: `intestazione-cliente.schema.json`, `tabella-preventivo.schema.json`.* - **COMPLETATA** (Vedi directory `app/schemas/`)
    3.  **Definizione Schema JSON "Master":** Definire come i JSON modulari si aggregano nel JSON "master" del preventivo. - **COMPLETATA** (Vedi `app/schemas/preventivo_master.schema.json`)
    4.  **Design Template HTML/Jinja2:** Creare i file `.html` per ogni modulo, con i placeholder Jinja2 che corrispondono agli schemi JSON definiti. - **COMPLETATA** (Vedi directory `app/templates/preventivo/`)
    5.  **Design UI/UX:** Mockup per i form di input manuale, assicurandosi che i campi dei form corrispondano logicamente agli schemi JSON. Progettare l'interattività della tabella preventivo. - *DA INIZIARE*
    6.  Setup Ambiente di Sviluppo. - **COMPLETATO** (FastAPI, Jinja2, struttura base)
*   **Criteri di Completamento:** Schemi JSON documentati e validati, template HTML/Jinja2 pronti, mockup UI approvati. Ambiente di sviluppo pronto. - **COMPLETATA**

**Fase 1: MVP - Preventivatore Manuale Modulare (LLM-Ready)**
*   **Obiettivo:** Realizzare l'applicazione manuale per preventivi, utilizzando l'architettura modulare e JSON-centrica.
*   **Logica del Funzionamento (2 frasi):** L'utente compila i form, il backend valida (opzionale) e assembla i JSON modulari in un JSON master, quindi renderizza il preventivo. HTMX gestisce l'interattività, specialmente per la tabella delle voci.
*   **Dettagli Tecnici / Attività:**
    1.  **Backend:**
        *   API per CRUD preventivi e gestione dati profilo utente (dati azienda).
        *   Logica di assemblaggio dei JSON modulari (originati dai form) nel JSON "master".
        *   Endpoint che ricevono dati per singole voci/sezioni e restituiscono HTML parziale per HTMX.
        *   Integrazione Jinja2 per rendering con JSON master.
        *   Servizio esportazione PDF.
    2.  **Frontend:**
        *   Implementazione dei form di input per ogni modulo (cliente, voci, condizioni).
        *   Integrazione HTMX per:
            *   Aggiungere/modificare/eliminare voci della tabella preventivo.
            *   Aggiornare dinamicamente i totali.
            *   Caricare/salvare altre sezioni del preventivo (es. dati cliente).
        *   Utilizzo di Alpine.js per interazioni UI locali (es. mostrare/nascondere form modali per aggiungere voci).
    3.  **Database:** Implementazione schemi per Utenti, DatiAzienda, PreventiviSalvati (con JSON master).
*   **Criteri di Completamento:** L'utente può creare, modificare, salvare, caricare ed esportare in PDF un preventivo completo. L'interfaccia è reattiva. *Il JSON master generato è ben strutturato e pronto per essere, in futuro, generato da un LLM.*
Use code with caution.
**Fase 2:** Integrazione LLM - Livello 1 (Automazione Input tramite LLM)
*   **Obiettivo:** "Attivare" l'LLM per popolare i JSON modulari basandosi sull'input utente in linguaggio naturale.
*   **Logica del Funzionamento (2 frasi):** L'utente fornisce testo; un nuovo servizio LLM nel backend lo elabora, generando i JSON modulari. Questi JSON alimentano il sistema di assemblaggio e rendering esistente, esattamente come facevano i dati dai form manuali.
*   **Dettagli Tecnici / Attività:**
    1.  **Backend (Nuovo Servizio LLM):**
        *   Endpoint API per ricevere input testuale utente.
        *   Logica di "dispatching" e prompt engineering:
            *   Inviare porzioni dell'input utente (o l'intero input con istruzioni specifiche) a un LLM per generare il JSON per *ciascun modulo rilevante*, fornendo lo schema JSON del modulo come parte del prompt.
            *   Esempio: "Utente dice: 'Preventivo per Mario Rossi di Azienda X, sito web 1000€'. Estrai dati per `intestazione-cliente.schema.json`. Estrai dati per `tabella-preventivo.schema.json`."
        *   Validazione dell'output JSON dell'LLM rispetto agli schemi modulari.
        *   Passaggio dei JSON modulari validati (generati dall'LLM) alla logica di assemblaggio JSON esistente (Fase 1).
    2.  **Frontend:**
        *   Nuova interfaccia per l'input in linguaggio naturale.
        *   Visualizzazione della "bozza" generata dall'LLM (che è di fatto il preventivo renderizzato dal sistema di Fase 1, ma con dati LLM).
        *   L'utente utilizza gli stessi controlli interattivi di Fase 1 (basati su HTMX) per modificare/correggere l'output dell'LLM.
*   **Criteri di Completamento:** L'utente può descrivere un preventivo in linguaggio naturale, l'LLM popola i dati, e il sistema genera un preventivo modificabile. Il "plug-in" dell'LLM è avvenuto con successo grazie all'architettura preesistente.
Use code with caution.
**Fase 3:** Funzionalità LLM Avanzate e Rifinitura Continua
*   (Come nel documento precedente: LLM0 per composizione, LLM CSS, amministrazione moduli avanzata, ottimizzazioni, feedback).
Use code with caution.
8. Modello Dati e Struttura JSON (Cruciale per LLM-Readiness)
Logica del Funzionamento (2 frasi):
La struttura dati, specialmente gli schemi JSON per ogni modulo e il JSON "master" che li aggrega, è il cuore dell'approccio "LLM-ready". Definiscono chiaramente cosa l'LLM deve produrre e cosa il sistema manuale deve gestire.
Dettagli Tecnici:
Schemi JSON Modulari: Ripetere l'importanza di avere file *.schema.json (o definizioni equivalenti) per intestazione-cliente, voce-preventivo, condizioni-generali, ecc. Questi schemi includeranno tipi di dati, campi richiesti, e descrizioni. Questi schemi saranno usati per validare l'input manuale e, soprattutto, per istruire e validare l'output dell'LLM.
JSON "Master" del Preventivo: La sua struttura deve essere un'aggregazione logica dei JSON modulari. Esempio fornito precedentemente, con chiavi di primo livello che raggruppano i dati per modulo (es. preventivo_master.cliente_destinatario conterrà i dati conformi a intestazione-cliente.schema.json).
Database: La tabella PreventiviSalvati memorizzerà il JSON "master". La definizione dei moduli nel DB includerà un riferimento o il contenuto del loro schema JSON.
9. Considerazioni per l'Integrazione LLM Futura
Contratto Rigido tramite Schemi: La stretta aderenza agli schemi JSON da parte dell'LLM sarà fondamentale. Tecniche come fornire lo schema nel prompt, usare funzioni/tool calling degli LLM (se disponibili e adatti), o avere un passo di validazione/correzione post-generazione LLM saranno necessarie.
Prompt Engineering Iterativo: La qualità dell'output LLM dipenderà fortemente dalla qualità dei prompt. Questi richiederanno iterazione e test.
Gestione dell'Ambiguità: L'input utente può essere ambiguo. L'MVP non gestirà questa ambiguità (l'utente è preciso). L'LLM potrebbe necessitare di chiedere chiarimenti o fare assunzioni (che l'utente potrà poi correggere).
Interfaccia di Revisione: L'interfaccia utente sviluppata per l'MVP manuale (con HTMX per modifiche fini) è già un'eccellente interfaccia di revisione per l'output dell'LLM. 