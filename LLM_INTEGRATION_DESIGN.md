# DESIGN INTEGRAZIONE LLM - Sistema di Generazione Documenti Modulari

**Documento Operativo v1.0**  
**Data Creazione:** 2024-12-17  
**Stato:** Draft - In Definizione  
**Riferimento:** Complementa `context.md` - Fasi 2 e 3 dello sviluppo

---

## INDICE

1. [Visione Generale e Obiettivi](#1-visione-generale-e-obiettivi)
2. [Analisi Stato Attuale](#2-analisi-stato-attuale)
3. [Architettura Proposta per Integrazione LLM](#3-architettura-proposta-per-integrazione-llm)
4. [Componente 1: Sistema Template Documenti Personalizzabili](#4-componente-1-sistema-template-documenti-personalizzabili)
5. [Componente 2: Creazione Moduli Personalizzati tramite LLM](#5-componente-2-creazione-moduli-personalizzati-tramite-llm)
6. [Componente 3: Agente LLM Contestuale](#6-componente-3-agente-llm-contestuale)
7. [Modifiche al Modello Dati (Database)](#7-modifiche-al-modello-dati-database)
8. [Strategie di Prompting](#8-strategie-di-prompting)
9. [Flussi Utente e UI/UX](#9-flussi-utente-e-uiux)
10. [Implementazione Graduale (Roadmap)](#10-implementazione-graduale-roadmap)
11. [Rischi, Sfide e Mitigazioni](#11-rischi-sfide-e-mitigazioni)
12. [Note Tecniche e Considerazioni](#12-note-tecniche-e-considerazioni)

---

## 1. VISIONE GENERALE E OBIETTIVI

### Obiettivo Principale
Evolvere il sistema attuale da un preventivatore manuale modulare a una piattaforma di generazione documenti intelligente e completamente personalizzabile, dove gli LLM agiscono come assistenti contestuali in tre livelli di astrazione:

1. **Livello Dati**: Popolamento automatico dei JSON modulari
2. **Livello Template**: Composizione dinamica di template documenti personalizzati 
3. **Livello Moduli**: Creazione di nuovi moduli su misura tramite LLM

### Principi Guida
- **Modularità**: Mantenere l'architettura JSON-centrica esistente
- **Plug-and-Play**: Integrazione LLM non invasiva rispetto al sistema esistente
- **Granularità**: Controllo fine su ogni livello (dati, template, moduli)
- **Componibilità**: Documenti completamente personalizzabili dall'utente
- **Contestualità**: LLM che si adatta al contesto operativo

---

## 2. ANALISI STATO ATTUALE

### Architettura Esistente (Punti di Forza)
✅ **Backend FastAPI** con logica di assemblaggio JSON modulare  
✅ **Database PostgreSQL** con supporto JSONB per flessibilità  
✅ **Sistema Template Jinja2** modulare e ben strutturato  
✅ **Schemi JSON** definiti per ogni modulo (`app/schemas/`)  
✅ **Servizi specializzati** (PreventivoService, PDFExportService, Calculator)  
✅ **Frontend HTMX/Alpine.js** per interattività real-time  

### Struttura Moduli Attuali
```
Moduli Preventivo Esistenti:
├── intestazione_azienda      (+ schema JSON)
├── intestazione_cliente      (+ schema JSON)  
├── tabella_preventivo        (+ schema JSON)
├── riga_preventivo          (+ schema JSON)
├── sezione_totali           (+ schema JSON)
├── condizioni_generali      (+ schema JSON)
└── footer_preventivo        (+ schema JSON)
```

### Struttura Database Attuale
```sql
users (UUID, email, username, ...)
├── aziende (dati azienda denormalizzati)
└── preventivi (numero, oggetto, stato, dati_preventivo:JSONB)
```

### Gap per Integrazione LLM
❌ **Template documenti fissi**: Solo preventivi, struttura non configurabile  
❌ **Moduli statici**: Non è possibile creare nuovi moduli dinamicamente  
❌ **Mancanza servizio LLM**: Nessuna integrazione con AI/LLM  
❌ **Contesto utente limitato**: Non c'è gestione della personalizzazione avanzata  

---

## 3. ARCHITETTURA PROPOSTA PER INTEGRAZIONE LLM

### Overview Architetturale

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │  Document Composer│ │  Module Creator  │ │  AI Assistant    ││
│  │  (Template Mgmt) │ │  (Custom Modules)│ │  (Chat Interface)││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                 │
                        ┌─────────────────┐
                        │   HTMX LAYER    │
                        │ (Real-time UI)  │
                        └─────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND API LAYER                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐│
│  │Document Template│ │  Module Mgmt    │ │    LLM Service      ││
│  │    Service      │ │    Service      │ │  (Context Router)   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────────┘│
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐│
│  │  Existing:      │ │     JSON        │ │     Template        ││
│  │ Preventivo Svc  │ │  Assembly Svc   │ │   Rendering Svc     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐│
│  │  Document       │ │   Custom        │ │     User           ││
│  │  Templates      │ │   Modules       │ │   Preferences      ││
│  └─────────────────┘ └─────────────────┘ └─────────────────────┘│
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐│
│  │  Existing:      │ │   Existing:     │ │    Existing:       ││
│  │   Documents     │ │    Users        │ │     Aziende        ││
│  └─────────────────┘ └─────────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Nuovi Componenti Core

#### 3.1 LLM Service (Context Router)
**Responsabilità**: Orchestrare le chiamate LLM basate sul contesto
- **Data Population**: Input naturale → JSON modulari
- **Template Composition**: Descrizione documento → Configurazione template
- **Module Generation**: Specifiche utente → Nuovo modulo (Jinja + Schema)

#### 3.2 Document Template Service  
**Responsabilità**: Gestire template documenti personalizzabili
- CRUD template documenti utente
- Composizione dinamica moduli
- Gestione formati (A4 portrait/landscape, US Letter, etc.)

#### 3.3 Module Management Service
**Responsabilità**: Gestire moduli personalizzati
- Registrazione nuovi moduli nel sistema
- Validazione moduli generati da LLM  
- Versioning e compatibilità moduli

---

## 4. COMPONENTE 1: SISTEMA TEMPLATE DOCUMENTI PERSONALIZZABILI

### 4.1 Obiettivo
Permettere agli utenti di creare template di documento personalizzati componendo moduli esistenti in ordini diversi e con formati di pagina variabili.

### 4.2 Modello Dati

#### Tabella: `document_templates`
```sql
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(100) NOT NULL, -- 'preventivo', 'fattura', 'contratto', etc.
    
    -- Configurazione composizione moduli
    module_composition JSONB NOT NULL, -- Array ordinato di module_id/name
    
    -- Configurazione formato
    page_format VARCHAR(50) DEFAULT 'A4', -- A4, US_LETTER, A3, etc.
    page_orientation VARCHAR(20) DEFAULT 'portrait', -- portrait, landscape
    margins JSONB, -- {top: 1.2, right: 0.8, bottom: 1.2, left: 0.8} in cm
    
    -- CSS/Styling personalizzato (futuro)
    custom_styles TEXT,
    
    -- Metadati
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE, -- Per template condivisibili
    version INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indici
CREATE INDEX idx_doc_templates_user_id ON document_templates(user_id);
CREATE INDEX idx_doc_templates_type ON document_templates(document_type);
```

#### Esempio `module_composition` JSON:
```json
{
  "modules": [
    {
      "module_name": "intestazione_azienda",
      "order": 1,
      "enabled": true,
      "custom_config": {}
    },
    {
      "module_name": "intestazione_cliente", 
      "order": 2,
      "enabled": true,
      "custom_config": {}
    },
    {
      "module_name": "custom_intro_section",
      "order": 3,
      "enabled": true,
      "custom_config": {"background_color": "#f9f9f9"}
    },
    {
      "module_name": "tabella_preventivo",
      "order": 4,
      "enabled": true,
      "custom_config": {}
    },
    {
      "module_name": "sezione_totali",
      "order": 5,
      "enabled": true,
      "custom_config": {}
    },
    {
      "module_name": "condizioni_generali",
      "order": 6,
      "enabled": false,
      "custom_config": {}
    },
    {
      "module_name": "footer_preventivo",
      "order": 7,
      "enabled": true,
      "custom_config": {}
    }
  ]
}
```

### 4.3 Document Template Service

```python
class DocumentTemplateService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, user_id: str, template_data: DocumentTemplateCreate) -> DocumentTemplate:
        """Crea un nuovo template documento"""
        pass
    
    def get_user_templates(self, user_id: str, document_type: Optional[str] = None) -> List[DocumentTemplate]:
        """Recupera template utente"""
        pass
    
    def compose_document(self, template_id: str, document_data: Dict) -> str:
        """Genera HTML del documento usando il template specificato"""
        # 1. Carica configurazione template
        # 2. Ordina moduli secondo module_composition
        # 3. Renderizza ciascun modulo con i dati appropriati
        # 4. Combina in documento finale con CSS per formato/orientamento
        pass
    
    def validate_module_composition(self, composition: Dict) -> bool:
        """Valida che tutti i moduli referenziati esistano"""
        pass
```

### 4.4 Interfaccia Utente - Template Composer

**Pagina: `/templates/composer`**

- **Drag & Drop Interface**: Lista moduli disponibili + area di composizione
- **Preview Live**: Anteprima documento mentre si compone
- **Format Settings**: Selezione formato pagina, orientamento, margini
- **Save Template**: Salvataggio template con nome e descrizione

---

## 5. COMPONENTE 2: CREAZIONE MODULI PERSONALIZZATI TRAMITE LLM

### 5.1 Obiettivo
Permettere la creazione di moduli completamente personalizzati attraverso l'assistenza di LLM, mantenendo la compatibilità con il sistema esistente.

### 5.2 Modello Dati

#### Tabella: `custom_modules`
```sql
CREATE TABLE custom_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    module_name VARCHAR(255) NOT NULL, -- nome_modulo_custom
    display_name VARCHAR(255) NOT NULL, -- Nome human-readable
    description TEXT,
    
    -- Template Jinja2 del modulo
    template_content TEXT NOT NULL,
    
    -- Schema JSON per i dati di input
    json_schema JSONB NOT NULL,
    
    -- Metadati modulo
    category VARCHAR(100), -- 'header', 'body', 'footer', 'table', 'custom'
    tags TEXT[], -- array di tag per ricerca
    
    -- Stato e validazione
    status VARCHAR(50) DEFAULT 'draft', -- draft, validated, active, deprecated
    validation_errors JSONB, -- errori di validazione se presente
    
    -- Generazione LLM tracking
    generated_by_llm BOOLEAN DEFAULT FALSE,
    llm_prompt_used TEXT, -- prompt originale per debugging
    llm_model_used VARCHAR(100), -- modello LLM utilizzato
    
    -- Versioning
    version INTEGER DEFAULT 1,
    parent_module_id UUID REFERENCES custom_modules(id), -- per versioning
    
    -- Condivisione
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indici
CREATE INDEX idx_custom_modules_user_id ON custom_modules(user_id);
CREATE INDEX idx_custom_modules_name ON custom_modules(module_name);
CREATE INDEX idx_custom_modules_category ON custom_modules(category);
CREATE UNIQUE INDEX idx_custom_modules_user_name ON custom_modules(user_id, module_name);
```

### 5.3 Module Generation Service

```python
class ModuleGenerationService:
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
    
    async def generate_module_from_description(
        self, 
        user_id: str, 
        description: str, 
        module_type: str = "custom"
    ) -> CustomModule:
        """
        Genera un nuovo modulo usando LLM basato sulla descrizione utente
        """
        # 1. Prompt engineering per generazione
        # 2. Chiamata LLM per ottenere template Jinja + schema JSON
        # 3. Validazione output LLM
        # 4. Registrazione modulo nel database
        # 5. Test rendering modulo
        pass
    
    def validate_custom_module(self, template_content: str, json_schema: Dict) -> Dict:
        """Valida template Jinja e schema JSON generati"""
        pass
    
    def register_module(self, module_data: CustomModuleCreate) -> CustomModule:
        """Registra un nuovo modulo nel sistema"""
        pass
    
    def test_module_rendering(self, module: CustomModule, test_data: Dict) -> str:
        """Testa il rendering del modulo con dati di esempio"""
        pass
```

### 5.4 Prompting Strategy per Module Generation

#### Template del Prompt per LLM:
```
Sei un esperto sviluppatore di template Jinja2 e schemi JSON per un sistema di generazione documenti modulari.

CONTESTO:
L'utente vuole creare un modulo personalizzato per documenti (preventivi, fatture, contratti, etc.).
Il modulo deve essere compatibile con il nostro sistema che usa:
- Template Jinja2 per il rendering HTML
- Schemi JSON per definire la struttura dati di input
- CSS integrato nel template per styling

RICHIESTA UTENTE: 
"{user_description}"

COMPITO:
Genera un modulo completo che includa:

1. TEMPLATE JINJA2:
- HTML valido con CSS integrato (tag <style>)
- Variabili Jinja2 che corrispondono allo schema JSON
- Responsive design compatibile con formato A4
- Stile coerente con design pulito e professionale

2. SCHEMA JSON:
- Schema JSON valido (JSON Schema v7)
- Campi che corrispondono alle variabili Jinja2
- Tipi di dati appropriati
- Descrizioni chiare per ogni campo
- Validazioni appropriate (required, format, etc.)

VINCOLI:
- Il template deve essere autonomo (CSS integrato)
- Usa solo variabili definite nello schema JSON
- Mantieni struttura pulita e professionale
- Optimizza per stampa e visualizzazione web

OUTPUT FORMAT:
Restituisci la risposta come JSON con questa struttura:
{
  "template_content": "<!-- HTML template Jinja2 -->",
  "json_schema": { /* schema JSON completo */ },
  "suggested_name": "nome_modulo_suggerito",
  "category": "header|body|footer|table|custom",
  "description": "Descrizione breve del modulo"
}
```

### 5.5 Interfaccia Utente - Module Creator

**Pagina: `/modules/creator`**

1. **AI Assistant Chat**: Interface conversazionale con LLM
2. **Module Preview**: Anteprima live del modulo generato
3. **Schema Editor**: Editor JSON per lo schema dati 
4. **Template Editor**: Editor Jinja2 con syntax highlighting
5. **Test Section**: Form generato automaticamente dallo schema per testare
6. **Validation Panel**: Errori e suggerimenti di validazione

---

## 6. COMPONENTE 3: AGENTE LLM CONTESTUALE

### 6.1 Obiettivo  
Creare un agente LLM intelligente che comprende il contesto dell'utente e può assistere in diversi scenari: popolamento dati, composizione template, creazione moduli.

### 6.2 LLM Service Architecture

```python
class LLMService:
    def __init__(self, openai_client, anthropic_client=None):
        self.openai = openai_client
        self.anthropic = anthropic_client
        self.context_manager = ContextManager()
    
    async def route_request(self, user_input: str, context: Dict) -> LLMResponse:
        """
        Router principale che determina il tipo di richiesta e chiama il giusto handler
        """
        intent = await self._classify_intent(user_input, context)
        
        match intent:
            case "data_population":
                return await self._handle_data_population(user_input, context)
            case "template_composition":
                return await self._handle_template_composition(user_input, context)
            case "module_generation":
                return await self._handle_module_generation(user_input, context)
            case "general_assistance":
                return await self._handle_general_assistance(user_input, context)
    
    async def _classify_intent(self, user_input: str, context: Dict) -> str:
        """Classifica l'intent dell'utente usando LLM"""
        pass
    
    async def _handle_data_population(self, user_input: str, context: Dict) -> DataPopulationResponse:
        """Gestisce popolamento dati per documenti esistenti"""
        # Identifica quali moduli servono dati
        # Genera JSON per ciascun modulo rilevante
        # Valida output contro schemi esistenti
        pass
    
    async def _handle_template_composition(self, user_input: str, context: Dict) -> TemplateCompositionResponse:
        """Gestisce richieste di composizione template documento"""
        # Suggerisce configurazione moduli
        # Propone ordine e formattazione
        pass
    
    async def _handle_module_generation(self, user_input: str, context: Dict) -> ModuleGenerationResponse:
        """Gestisce creazione nuovi moduli personalizzati"""
        # Usa ModuleGenerationService
        pass

class ContextManager:
    """Gestisce il contesto della conversazione e dello stato utente"""
    
    def get_user_context(self, user_id: str) -> Dict:
        """Recupera contesto utente completo"""
        return {
            "current_document": "...",  # documento in editing
            "available_modules": "...",  # moduli disponibili
            "user_templates": "...",     # template utente
            "recent_activity": "...",    # attività recenti
            "preferences": "..."         # preferenze utente
        }
    
    def update_context(self, user_id: str, new_context: Dict):
        """Aggiorna contesto conversazione"""
        pass
```

### 6.3 Context-Aware Prompting

Il servizio LLM mantiene consapevolezza di:
- **Documento corrente** in editing (tipo, moduli, dati parziali)
- **Moduli disponibili** (built-in + custom utente)
- **Template utente** (configurazioni salvate)
- **Storico conversazione** (richieste precedenti)
- **Preferenze utente** (stili, formati preferiti)

---

## 7. MODIFICHE AL MODELLO DATI (DATABASE)

### 7.1 Nuove Tabelle

Oltre alle tabelle `document_templates` e `custom_modules` già specificate:

#### Tabella: `user_preferences`
```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    
    -- Preferenze UI
    default_page_format VARCHAR(50) DEFAULT 'A4',
    default_orientation VARCHAR(20) DEFAULT 'portrait',
    preferred_language VARCHAR(10) DEFAULT 'it',
    
    -- Preferenze LLM
    preferred_llm_model VARCHAR(100) DEFAULT 'gpt-4',
    llm_temperature DECIMAL(2,1) DEFAULT 0.7,
    auto_suggestions BOOLEAN DEFAULT TRUE,
    
    -- Preferenze documento
    default_document_template_id UUID REFERENCES document_templates(id),
    auto_save_interval INTEGER DEFAULT 30, -- secondi
    
    -- Impostazioni privacy
    allow_public_templates BOOLEAN DEFAULT FALSE,
    data_retention_days INTEGER DEFAULT 365,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabella: `llm_conversations`
```sql
CREATE TABLE llm_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    session_id VARCHAR(255) NOT NULL, -- per raggruppare conversazioni
    
    -- Messaggio
    message_type VARCHAR(50) NOT NULL, -- 'user_input', 'llm_response', 'system'
    message_content TEXT NOT NULL,
    
    -- Contesto al momento del messaggio
    context_snapshot JSONB,
    
    -- Metadati LLM (per responses)
    llm_model VARCHAR(100),
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    
    -- Risultati (per richieste che producono output)
    generated_data JSONB, -- JSON modulari generati, moduli creati, etc.
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_llm_conversations_session ON llm_conversations(session_id);
CREATE INDEX idx_llm_conversations_user ON llm_conversations(user_id);
```

### 7.2 Estensioni Tabelle Esistenti

#### Estensione `preventivi` → `documents`
```sql
-- Rinomina e generalizza per supportare più tipi documento
ALTER TABLE preventivi RENAME TO documents;

-- Aggiungi nuovi campi
ALTER TABLE documents ADD COLUMN document_type VARCHAR(100) DEFAULT 'preventivo';
ALTER TABLE documents ADD COLUMN template_id UUID REFERENCES document_templates(id);
ALTER TABLE documents ADD COLUMN format_config JSONB; -- override formato per questo documento
```

---

## 8. STRATEGIE DI PROMPTING

### 8.1 Intent Classification Prompt

```
Analizza la seguente richiesta utente e classifica l'intent principale:

RICHIESTA: "{user_input}"

CONTESTO: 
- Utente sta usando: {current_context}
- Documento corrente: {current_document_type}
- Moduli disponibili: {available_modules}

OPZIONI INTENT:
1. "data_population" - Vuole popolare/compilare dati per un documento
2. "template_composition" - Vuole creare/modificare template di documento  
3. "module_generation" - Vuole creare nuovi moduli personalizzati
4. "general_assistance" - Domande generali o aiuto navigazione

RISPOSTA: Restituisci solo il nome dell'intent (senza virgolette).
```

### 8.2 Data Population Prompt

```
Sei un assistente AI specializzato nell'estrazione e strutturazione dati per documenti aziendali.

RICHIESTA UTENTE: "{user_input}"

MODULI DOCUMENTO ATTIVI:
{active_modules_list}

COMPITO:
Analizza la richiesta ed estrai i dati per popolare i moduli JSON appropriati.

PER OGNI MODULO RILEVANTE:
- Identifica il modulo corrispondente
- Estrai solo i dati pertinenti dalla richiesta
- Struttura secondo lo schema JSON del modulo
- Se mancano dati necessari, imposta campi come null

SCHEMI DISPONIBILI:
{json_schemas}

OUTPUT FORMAT:
{
  "modules_populated": [
    {
      "module_name": "nome_modulo",
      "data": { /* dati JSON conformi allo schema */ },
      "confidence": 0.95, /* 0-1 fiducia nell'estrazione */
      "missing_fields": ["campo1", "campo2"] /* campi non estratti */
    }
  ],
  "suggestions": ["Suggerimento per completare dati mancanti..."]
}
```

### 8.3 Template Composition Prompt

```
Sei un consulente esperto nella progettazione di template per documenti aziendali.

RICHIESTA: "{user_input}"

MODULI DISPONIBILI:
{available_modules}

TEMPLATE ESISTENTI UTENTE:
{user_templates}

COMPITO:
Suggerisci una configurazione di template documento che soddisfi la richiesta.

CONSIDERA:
- Tipo di documento (preventivo, fattura, contratto, etc.)
- Settore aziendale dell'utente
- Requisiti legali e convenzioni del settore
- Best practices per il tipo di documento

OUTPUT FORMAT:
{
  "suggested_template": {
    "name": "Nome Template Suggerito",
    "description": "Descrizione template",
    "document_type": "tipo_documento", 
    "module_composition": {
      "modules": [
        {
          "module_name": "nome_modulo",
          "order": 1,
          "enabled": true,
          "justification": "Perché questo modulo è importante"
        }
      ]
    },
    "page_format": "A4",
    "page_orientation": "portrait"
  },
  "alternatives": [
    /* alternative configuration options */
  ],
  "explanation": "Spiegazione delle scelte fatte"
}
```

---

## 9. FLUSSI UTENTE E UI/UX

### 9.1 Flusso Template Composer

1. **Dashboard** → "Crea Nuovo Template"
2. **Template Composer Interface**:
   - Sidebar sinistra: Moduli disponibili (built-in + custom)
   - Area centrale: Canvas di composizione (drag & drop)
   - Sidebar destra: Configurazione formato + preview settings
3. **Drag & Drop**: Trascina moduli nel canvas, riordina
4. **Live Preview**: Anteprima documento durante composizione
5. **AI Assistant (opzionale)**: Chat per suggerimenti configurazione
6. **Save Template**: Nome, descrizione, set as default

### 9.2 Flusso Module Creator

1. **Modules Dashboard** → "Crea Modulo Personalizzato"
2. **AI-Assisted Creation**:
   - Chat interface: "Descrivi il modulo che vuoi creare"
   - LLM genera template + schema
   - Preview automatico del modulo generato
3. **Manual Refinement**:
   - Editor split: Template Jinja | Schema JSON
   - Live preview con form di test generato automaticamente
4. **Validation & Testing**:
   - Validazione automatica template e schema
   - Test con dati di esempio
5. **Save & Register**: Modulo pronto per uso in template

### 9.3 Flusso Document Creation con AI

1. **Dashboard** → "Nuovo Documento" 
2. **Template Selection**: Scegli template o "Crea con AI"
3. **AI Document Assistant**:
   - Input naturale: "Crea preventivo per sito web azienda X, budget 5000€"
   - LLM popola automaticamente tutti i moduli
   - Preview documento generato
4. **Manual Refinement**: 
   - Form editing tradizionale per correzioni
   - Richieste aggiuntive all'AI: "Aggiungi sezione manutenzione"
5. **Finalize**: Save, export PDF, send

### 9.4 UI Components Nuovi

#### AI Chat Widget (Persistente)
- **Posizione**: Bottom-right corner, expandable
- **Contesto**: Sempre consapevole della pagina/documento corrente
- **Features**: Persistent conversation, quick suggestions, voice input

#### Template Composer Canvas
- **Drag & Drop**: Sortable.js per riordinamento moduli
- **Visual Preview**: Split view composer/preview
- **Module Configuration**: Popover settings per ogni modulo

#### Module Editor
- **Split Pane**: Template editor (left) | Schema editor (right)
- **Live Preview**: Bottom pane con test form + rendered output
- **Syntax Highlighting**: Monaco Editor per Jinja2 e JSON

---

## 10. IMPLEMENTAZIONE GRADUALE (ROADMAP)

### Fase 2a: Template Documenti Personalizzabili (4-6 settimane)

**Week 1-2: Database & Backend**
- [ ] Implementa tabelle `document_templates`, `user_preferences`
- [ ] Crea `DocumentTemplateService`
- [ ] Estendi rendering engine per template dinamici
- [ ] API endpoints per gestione template

**Week 3-4: Frontend Template Composer**
- [ ] UI Template Composer con drag & drop
- [ ] Preview live documents
- [ ] Gestione formato pagina e orientamento
- [ ] Salvataggio e caricamento template

**Week 5-6: Testing & Refinement**
- [ ] Test con vari tipi documento
- [ ] Ottimizzazione performance rendering
- [ ] UI/UX improvements

### Fase 2b: Integrazione LLM Base (3-4 settimane)

**Week 1: LLM Service Foundation**
- [ ] Setup LLM client (OpenAI API)
- [ ] Implementa `LLMService` base con intent classification
- [ ] Context manager per stato conversazione
- [ ] API endpoints per chat LLM

**Week 2-3: Data Population LLM**  
- [ ] Prompt engineering per data extraction
- [ ] Integrazione con schemi JSON esistenti
- [ ] Validazione output LLM
- [ ] UI chat widget per document creation

**Week 4: Testing & Integration**
- [ ] Test data population con vari input types
- [ ] Integration testing con document creation flow
- [ ] Error handling e fallbacks

### Fase 2c: Module Creation LLM (4-5 settimane)

**Week 1-2: Custom Modules Database & Service**
- [ ] Implementa tabella `custom_modules`
- [ ] Crea `ModuleGenerationService`
- [ ] Module validation e registration system
- [ ] API endpoints per custom modules

**Week 3-4: LLM Module Generation**
- [ ] Advanced prompting per module generation  
- [ ] Template Jinja2 + JSON Schema generation
- [ ] Validation pipeline per LLM output
- [ ] UI Module Creator interface

**Week 5: Testing & Refinement**
- [ ] Test creazione moduli vari tipi
- [ ] Validation robustness testing
- [ ] UI improvements e UX flow

### Fase 3: Agente LLM Avanzato (6-8 settimane)

**Week 1-2: Context-Aware LLM**
- [ ] Advanced context management
- [ ] Multi-turn conversation handling
- [ ] User preference learning
- [ ] Conversation persistence (`llm_conversations`)

**Week 3-4: Template Composition LLM**
- [ ] LLM template suggestion engine
- [ ] Integration con Template Composer
- [ ] Advanced prompting per document design

**Week 5-6: AI Assistant Enhancement** 
- [ ] Proactive suggestions
- [ ] Help system integration
- [ ] Voice input support (opzionale)
- [ ] Advanced UI for AI interactions

**Week 7-8: Polish & Optimization**
- [ ] Performance optimization
- [ ] Advanced error handling
- [ ] User onboarding per AI features
- [ ] Analytics e usage tracking

---

## 11. RISCHI, SFIDE E MITIGAZIONI

### 11.1 Rischi Tecnici

#### **Qualità Output LLM**
- **Rischio**: LLM genera template Jinja2 o JSON Schema non validi
- **Mitigazione**: 
  - Validation pipeline robusto
  - Fallback su template base se generazione fallisce
  - Iterative prompting per correzioni
  - Testing automatizzato output LLM

#### **Performance Template Dynamici** 
- **Rischio**: Rendering lento con template complessi e composizione dinamica
- **Mitigazione**:
  - Caching template compiled
  - Lazy loading moduli non utilizzati
  - Database query optimization
  - Async rendering per preview

#### **Scalabilità LLM Calls**
- **Rischio**: Costi e latenza chiamate LLM
- **Mitigazione**:
  - Rate limiting intelligente
  - Caching risposte LLM comuni
  - Modelli LLM più piccoli per task semplici
  - Batch processing quando possibile

### 11.2 Rischi UX/Product

#### **Complessità Interfaccia**
- **Rischio**: Troppa flessibilità confonde utenti
- **Mitigazione**:
  - Onboarding guidato
  - Template default semplici
  - Progressive disclosure funzionalità avanzate
  - Help contestuale

#### **Aspettative Irrealistiche LLM**
- **Rischio**: Utenti si aspettano AI perfecta
- **Mitigazione**:
  - Clear communication capacità/limiti AI
  - Interfaccia manual override sempre presente
  - Feedback loop per improvement
  - Esempi e best practices

### 11.3 Rischi Business

#### **Vendor Lock-in LLM**
- **Rischio**: Dipendenza da specifico provider LLM
- **Mitigazione**:
  - Architettura multi-provider (OpenAI + Anthropic + local)
  - Standard interface `LLMService` 
  - Fallback su modelli più semplici

#### **Data Privacy**
- **Rischio**: Dati sensibili inviati a LLM esterni
- **Mitigazione**:
  - Data anonymization/sanitization
  - Opt-in per feature AI
  - Local LLM options per dati sensibili
  - Clear privacy policy

---

## 12. NOTE TECNICHE E CONSIDERAZIONI

### 12.1 Compatibilità Backward

Tutte le nuove funzionalità devono mantenere 100% compatibilità con:
- Preventivi esistenti nel database
- Template `preventivo_unificato.html` attuale
- Schemi JSON modulari esistenti
- API endpoints attuali

### 12.2 Testing Strategy

#### Unit Tests
- LLM prompt/response validation
- Template composition logic
- Module generation validation
- JSON Schema compliance

#### Integration Tests  
- End-to-end document creation flows
- LLM service integration
- Database operations complex queries
- Frontend component interactions

#### User Acceptance Testing
- Usability AI interfaces
- Performance template rendering
- Mobile responsiveness nuove UI

### 12.3 Deployment Considerations

#### Environment Variables
```env
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
LLM_DEFAULT_MODEL=gpt-4
LLM_FALLBACK_MODEL=gpt-3.5-turbo

# Feature Flags
ENABLE_LLM_FEATURES=true
ENABLE_CUSTOM_MODULES=true
ENABLE_AI_CHAT=true

# Performance
LLM_RATE_LIMIT_RPM=60
TEMPLATE_CACHE_TTL=3600
```

#### Infrastructure
- Redis per caching template e sessioni LLM
- Background job queue per LLM processing async
- CDN per static assets template custom
- Monitoring LLM usage e costs

### 12.4 Security

- Input sanitization per template generati LLM
- XSS protection template custom Jinja2
- Rate limiting API LLM per prevenire abuse
- Audit log per azioni AI sensitive
- Permission system per condivisione template/moduli

---

## CONCLUSIONI

Questo design rappresenta un'evoluzione significativa del sistema esistente verso una piattaforma di generazione documenti veramente intelligente e flessibile. L'approccio graduale permette di validare ogni componente prima di procedere al successivo, mantenendo sempre un sistema funzionante.

Le fondamenta architetturali attuali (JSON modulare, template Jinja2, database JSONB) si prestano perfettamente a questa evoluzione, rendendo l'integrazione LLM veramente "plug-and-play" come originariamente progettato.

Il risultato finale sarà un sistema che mantiene la precisione e controllo del workflow manuale, aggiungendo l'intelligenza e flessibilità degli LLM per velocizzare e semplificare drasticamente la creazione di documenti aziendali personalizzati. 