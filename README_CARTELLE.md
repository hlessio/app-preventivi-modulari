# Sistema Cartelle - App Preventivi

## 📁 Panoramica

Il sistema delle cartelle permette di organizzare i preventivi in categorie personalizzabili, migliorando la gestione e la ricerca dei documenti.

## 🚀 Funzionalità Implementate

### ✅ Gestione Cartelle
- **Creazione cartelle** con nome, descrizione, colore e icona personalizzabili
- **Modifica cartelle** esistenti
- **Eliminazione cartelle** con spostamento automatico dei preventivi
- **Visualizzazione gerarchica** nella sidebar

### ✅ Organizzazione Preventivi
- **Spostamento preventivi** tra cartelle tramite drag & drop o menu
- **Filtro per cartella** nella vista principale
- **Conteggio preventivi** per ogni cartella
- **Vista "Senza cartella"** per preventivi non organizzati

### ✅ Interfaccia Utente
- **Sidebar dedicata** con lista cartelle
- **Colori personalizzati** per identificazione visiva
- **Icone FontAwesome** per categorizzazione
- **Badge cartella** sui preventivi
- **Modali responsive** per gestione cartelle

## 🗄️ Struttura Database

### Tabella `cartelle`
```sql
CREATE TABLE cartelle (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    nome VARCHAR(255) NOT NULL,
    descrizione TEXT,
    colore VARCHAR(7), -- Hex color (#FF5733)
    icona VARCHAR(50), -- FontAwesome class
    parent_id UUID REFERENCES cartelle(id), -- Per cartelle annidate (futuro)
    ordine INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Aggiornamento Tabella `preventivi`
```sql
ALTER TABLE preventivi 
ADD COLUMN cartella_id UUID REFERENCES cartelle(id);
```

## 🔌 API Endpoints

### Cartelle
- `GET /cartelle` - Lista tutte le cartelle dell'utente
- `POST /cartelle` - Crea una nuova cartella
- `GET /cartelle/{id}` - Ottiene una cartella specifica
- `PUT /cartelle/{id}` - Aggiorna una cartella
- `DELETE /cartelle/{id}` - Elimina una cartella
- `POST /cartelle/sposta-preventivi` - Sposta preventivi in massa

### Preventivi con Cartelle
- `GET /preventivi/con-cartelle` - Lista preventivi con info cartelle
- `GET /cartelle/{id}/preventivi` - Preventivi di una cartella specifica
- `POST /preventivo/{id}/sposta-cartella` - Sposta un preventivo

## 🎨 Personalizzazione

### Colori Disponibili
Le cartelle supportano qualsiasi colore esadecimale. Esempi:
- `#007bff` - Blu
- `#28a745` - Verde
- `#dc3545` - Rosso
- `#ffc107` - Giallo
- `#6f42c1` - Viola

### Icone Disponibili
Icone FontAwesome predefinite:
- `fas fa-folder` - Cartella standard
- `fas fa-briefcase` - Business
- `fas fa-star` - Importante
- `fas fa-heart` - Preferiti
- `fas fa-home` - Casa/Personale
- `fas fa-building` - Azienda
- `fas fa-users` - Team
- `fas fa-cog` - Configurazione

## 🧪 Test del Sistema

### Avvio Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Esecuzione Test
```bash
python test_cartelle_system.py
```

### Test Manuali
1. Apri http://localhost:8000
2. Crea alcune cartelle di test
3. Sposta preventivi nelle cartelle
4. Testa i filtri per cartella
5. Verifica la persistenza dei dati

## 📱 Utilizzo Interfaccia

### Creazione Cartella
1. Clicca "Nuova" nella sidebar cartelle
2. Inserisci nome (obbligatorio)
3. Aggiungi descrizione (opzionale)
4. Scegli colore e icona
5. Clicca "Crea Cartella"

### Spostamento Preventivi
1. Nella vista preventivi, clicca "Cartella" su un preventivo
2. Seleziona la cartella di destinazione
3. Il preventivo viene spostato automaticamente

### Filtro per Cartella
1. Clicca su una cartella nella sidebar
2. La vista si aggiorna mostrando solo i preventivi di quella cartella
3. Clicca "Tutti i preventivi" per rimuovere il filtro

## 🔧 Configurazione

### Variabili Ambiente
Nessuna configurazione aggiuntiva richiesta. Il sistema utilizza le stesse impostazioni database dell'applicazione principale.

### Migrazione Database
```bash
alembic upgrade head
```

## 🐛 Troubleshooting

### Errori Comuni

**Cartella non trovata**
- Verifica che l'ID cartella sia corretto
- Controlla che l'utente abbia accesso alla cartella

**Preventivo non si sposta**
- Verifica che il preventivo esista
- Controlla i permessi utente
- Verifica che la cartella di destinazione esista

**Sidebar non carica cartelle**
- Controlla la console browser per errori JavaScript
- Verifica che l'endpoint `/cartelle` risponda correttamente
- Controlla la connessione database

### Log Debug
Abilita logging dettagliato in `app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Prossimi Sviluppi

### Funzionalità Pianificate
- [ ] **Cartelle annidate** (sottocartelle)
- [ ] **Drag & drop** diretto nella sidebar
- [ ] **Condivisione cartelle** tra utenti
- [ ] **Template cartelle** predefiniti
- [ ] **Esportazione** cartelle in PDF/Excel
- [ ] **Statistiche** per cartella
- [ ] **Backup/Restore** configurazione cartelle

### Miglioramenti UX
- [ ] **Ricerca** all'interno delle cartelle
- [ ] **Ordinamento** cartelle personalizzato
- [ ] **Temi** colore per cartelle
- [ ] **Shortcuts** tastiera
- [ ] **Notifiche** spostamenti
- [ ] **Undo/Redo** operazioni

## 📞 Supporto

Per problemi o domande sul sistema cartelle:
1. Controlla questo README
2. Esegui i test automatici
3. Verifica i log dell'applicazione
4. Controlla la documentazione API

---

**Versione:** 1.0.0  
**Data:** Gennaio 2025  
**Compatibilità:** Python 3.8+, PostgreSQL 12+ 