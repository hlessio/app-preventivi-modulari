# Sistema Template Modulare - Guida Completa

## Panoramica

Il sistema template dell'applicazione preventivi implementa un motore modulare e flessibile che permette agli utenti di creare documenti personalizzati attraverso template configurabili. Il sistema è progettato con architettura "LLM-ready" e supporta la composizione dinamica di moduli.

## Architettura del Sistema

### 1. Componenti Principali

#### Backend Services
- **`DocumentTemplateService`**: Gestisce CRUD template, validazione e composizione
- **`PreventivoService`**: Integrato con template per salvataggio e caricamento documenti
- **`PDFExportService`**: Genera PDF utilizzando template personalizzati

#### Database Schema
```sql
document_templates:
  - id (UUID)
  - user_id (UUID) 
  - name, description
  - document_type (es. "preventivo")
  - module_composition (JSON)
  - page_format, page_orientation, margins
  - custom_styles (CSS)
  - is_default, is_public, version
  - created_at, updated_at
```

#### Frontend Components
- **Template Composer**: UI drag & drop per creare template
- **Dashboard Template Selector**: Dropdown per scegliere template
- **Dynamic Form**: Form che mostra/nasconde sezioni in base al template

### 2. Moduli Disponibili

Il sistema supporta questi moduli per i preventivi:

| Modulo | Identificatore | Descrizione |
|--------|---------------|-------------|
| Dati Azienda | `intestazione_azienda` | Logo, ragione sociale, P.IVA |
| Dati Cliente | `intestazione_cliente` | Informazioni destinatario |
| Tabella Preventivo | `tabella_preventivo` | Voci con calcoli automatici |
| Condizioni Generali | `condizioni_generali` | Termini e condizioni |
| Footer | `footer_preventivo` | Note finali e firme |

## Flusso Utente Completo

### 1. Creazione Template (Template Composer)

1. **Accesso**: `/templates/composer`
2. **Configurazione**:
   - Nome e descrizione template
   - Formato pagina (A4, A3, Letter, Legal)
   - Orientamento (portrait/landscape)
   - Margini personalizzati
3. **Composizione Moduli**:
   - Drag & drop moduli disponibili
   - Attivazione/disattivazione moduli
   - Ordinamento priorità
4. **Anteprima Live**: Visualizzazione real-time del documento
5. **Salvataggio**: Persistenza configurazione nel database

### 2. Creazione Documento con Template

#### Workflow Migliorato (Dashboard → Form)

1. **Dashboard** (`/`):
   - Click "Nuovo Preventivo" → Dropdown template
   - Visualizzazione template disponibili con:
     - Nome e descrizione
     - Numero moduli attivi
     - Indicatore template default
     - Anteprima visuale

2. **Selezione Template**:
   - Click template → Redirect a `/preventivo/nuovo?template_id=XXX`
   - Template precaricato e applicato automaticamente

3. **Form Dinamico**:
   - Sezioni visibili solo se modulo abilitato nel template
   - Uso di Alpine.js `x-show` per controllo visibilità
   - Indicatori visivi template attivo e sezioni nascoste

#### Mapping Moduli → Sezioni Form

```javascript
const moduleFormMapping = {
    'intestazione_azienda': 'company-data-form',
    'intestazione_cliente': 'client-data-form', 
    'tabella_preventivo': 'line-items-form',
    'condizioni_generali': 'terms-conditions-form',
    'footer_preventivo': 'footer-form'
};
```

### 3. Gestione Template nel Form

Il form di creazione/modifica implementa logica dinamica:

```javascript
// Controllo visibilità moduli
isModuleVisible(moduleId) {
    if (!this.selectedTemplate) return true; // Default: tutto visibile
    const module = this.selectedTemplate.module_composition?.modules?.find(m => m.module_id === moduleId);
    return module?.enabled || false;
}

// Caricamento template preselezionato
async loadTemplateById(templateId) {
    const response = await fetch(`/templates/${templateId}?user_id=${this.userId}`);
    const template = await response.json();
    this.selectedTemplate = template;
    this.updateVisibleModules();
}
```

## API Endpoints

### Template Management

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/templates` | GET | Lista template utente |
| `/templates` | POST | Crea nuovo template |
| `/templates/{id}` | GET | Dettaglio template |
| `/templates/{id}` | PUT | Aggiorna template |
| `/templates/{id}` | DELETE | Elimina template |
| `/templates/default/{type}` | GET | Template default per tipo |
| `/templates/validate` | POST | Valida composizione moduli |

### Document Operations

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/preventivo/nuovo` | GET | Form nuovo (con template_id opzionale) |
| `/preventivo/visualizza` | POST | Rendering con template |
| `/preventivo/{id}/pdf` | GET | Export PDF con template |
| `/preventivo/preview` | POST | Anteprima template composer |

## Strutture Dati

### ModuleComposition Schema

```json
{
  "modules": [
    {
      "module_id": "intestazione_azienda",
      "enabled": true,
      "order": 1,
      "settings": {
        "show_logo": true,
        "show_contact_info": true
      }
    },
    {
      "module_id": "tabella_preventivo", 
      "enabled": true,
      "order": 2,
      "settings": {
        "show_quantities": true,
        "show_discounts": false
      }
    }
  ]
}
```

### Template Configuration

```json
{
  "id": "uuid",
  "name": "Template Minimo",
  "description": "Solo cliente e voci",
  "document_type": "preventivo",
  "module_composition": { /* vedi sopra */ },
  "page_format": "A4",
  "page_orientation": "portrait",
  "margins": {
    "top": 1.2,
    "bottom": 1.2, 
    "left": 0.8,
    "right": 0.8
  },
  "custom_styles": "/* CSS personalizzato */",
  "is_default": false
}
```

## Integrazione PDF

Il sistema genera PDF utilizzando WeasyPrint con template personalizzati:

```python
def genera_pdf_preventivo_con_template(self, preventivo_data, template):
    # 1. Componi dati secondo template
    composed_data = self.template_service.compose_document_from_template(
        template, preventivo_data.model_dump()
    )
    
    # 2. Renderizza HTML con template
    html_content = self.templates.get_template(
        "preventivo/preventivo_unificato.html"
    ).render(**composed_data)
    
    # 3. Applica stili CSS template + pagina
    css = self._build_css_for_template(template)
    
    # 4. Genera PDF
    document = HTML(string=html_content).render(stylesheets=[css])
    return document.write_pdf()
```

## Vantaggi dell'Architettura

### 1. User Experience
- **Workflow Intuitivo**: Selezione template nel punto logico (dashboard)
- **Form Pulito**: Solo sezioni rilevanti visibili
- **Anteprima Live**: Feedback immediato nel composer

### 2. Flessibilità
- **Template Illimitati**: Ogni utente può creare template personalizzati
- **Moduli Riutilizzabili**: Stessi moduli in configurazioni diverse
- **Extensibilità**: Facile aggiungere nuovi moduli

### 3. Performance
- **Lazy Loading**: Template caricati solo quando necessari
- **Caching**: Template riutilizzati tra sessioni
- **Validazione**: Controlli client + server side

### 4. LLM-Ready
- **Schema JSON**: Contratto chiaro per input/output LLM
- **Modularità**: LLM può generare singoli moduli
- **Composizione**: Assemblaggio automatico JSON → Template

## Template di Esempio

### Template Standard (Default)
- Tutti i moduli abilitati
- Layout tradizionale completo

### Template Minimo  
- Solo `intestazione_cliente` + `tabella_preventivo`
- Per preventivi semplificati

### Template Aziendale
- `intestazione_azienda` + `condizioni_generali` + `footer_preventivo`
- Focus su branding aziendale

## Sviluppi Futuri

### Funzionalità Pianificate
1. **Template Marketplace**: Condivisione template tra utenti
2. **Temi Visuali**: Preset colori e stili
3. **Template Condizionali**: Moduli visibili in base ai dati
4. **Integrazione LLM**: Generazione automatica template
5. **Template Versioning**: Gestione versioni e rollback

### Estensioni Tecniche
1. **Nuovi Tipi Documento**: Fatture, offerte, contratti
2. **Moduli Custom**: Editor per moduli personalizzati
3. **API Esterne**: Integrazione servizi terzi
4. **Multi-tenant**: Supporto organizzazioni

## Manutenzione

### Best Practices
- Backup regolari template utente
- Validazione composizioni pre-save
- Test compatibilità PDF multi-template
- Monitoring performance rendering

### Troubleshooting
- **Template non visibile**: Verificare user_id e document_type
- **PDF malformato**: Controllare custom_styles CSS
- **Moduli mancanti**: Validare module_composition
- **Performance lente**: Ottimizzare query template

Questo sistema rappresenta una soluzione completa e scalabile per la gestione template modulari, pronta per l'evoluzione verso funzionalità LLM avanzate. 