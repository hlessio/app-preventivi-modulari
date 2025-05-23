# Export PDF - Documentazione

## Panoramica

Il sistema di export PDF permette di generare documenti PDF professionali dei preventivi utilizzando **WeasyPrint**, una libreria Python per la conversione HTML to PDF.

## Funzionalità Implementate

### 1. **Servizio PDF (`app/services/pdf_export_service.py`)**
- **`PDFExportService`**: Classe principale per la generazione PDF
- **Template specifico per PDF**: `app/templates/preventivo/preventivo_pdf.html`
- **CSS ottimizzato per stampa**: Stili dedicati per formato A4 e stampa
- **Supporto per numerazione pagine**: Footer automatico con conteggio pagine

### 2. **Endpoint API**

#### POST `/preventivo/pdf`
Genera un PDF al volo dai dati forniti:
```bash
curl -X POST "http://localhost:8000/preventivo/pdf" \
     -H "Content-Type: application/json" \
     -d @preventivo_data.json \
     --output preventivo.pdf
```

#### GET `/preventivo/{id}/pdf`
Scarica il PDF di un preventivo salvato:
```bash
curl "http://localhost:8000/preventivo/12345/pdf?user_id=test-user" \
     --output preventivo_12345.pdf
```

### 3. **Interfaccia Utente**

#### Dashboard
- **Pulsante PDF** in ogni riga della tabella preventivi
- **Icona**: Arancione con icona `fa-file-pdf`
- **Azione**: Download diretto del PDF

#### Form Preventivo
- **Pulsante "Scarica PDF"** nella barra superiore
- **Logica intelligente**: 
  - Preventivo esistente → usa endpoint GET
  - Preventivo nuovo → usa endpoint POST con dati attuali

## Caratteristiche Tecniche

### Template PDF Ottimizzato
- **Layout A4**: Margini di 2cm su tutti i lati
- **Tipografia professionale**: Font DejaVu Sans per compatibilità
- **Intestazioni e piè di pagina**: Logo azienda e numerazione pagine
- **Tabelle responsive**: Layout adattivo per voci preventivo
- **Interruzioni di pagina intelligenti**: Evita suddivisioni indesiderate

### Stili CSS per Stampa
```css
@page {
    size: A4;
    margin: 2cm 1.5cm;
    @bottom-center {
        content: "Pagina " counter(page) " di " counter(pages);
    }
}
```

### Calcoli Automatici
- **Totali per riga**: Quantità × Prezzo × (1 - Sconto%)
- **Subtotale**: Somma di tutte le righe
- **IVA**: Calcolata automaticamente
- **Totale generale**: Subtotale + IVA

## Configurazione e Requisiti

### Dipendenze di Sistema (macOS)
```bash
# Installa le librerie necessarie
brew install pango gdk-pixbuf libffi

# Configura l'ambiente (usa lo script fornito)
./setup_weasyprint.sh

# Oppure manualmente:
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:/usr/local/lib:$DYLD_LIBRARY_PATH"
```

### Dipendenze Python
```bash
pip install weasyprint
```

## Test e Debugging

### Script di Test
```bash
# Esegui il test completo
python test_pdf.py
```

Il test genera:
- `test_preventivo.html` - Anteprima HTML per debugging
- `test_preventivo.pdf` - PDF finale generato

### Risoluzione Problemi Comuni

#### 1. Errore "cannot load library 'libgobject-2.0-0'"
**Soluzione**: Configurare le variabili d'ambiente
```bash
source setup_weasyprint.sh
```

#### 2. Font non trovati
**Problema**: WeasyPrint potrebbe non trovare i font di sistema
**Soluzione**: Il template usa `DejaVu Sans` che è incluso in WeasyPrint

#### 3. Layout rovinato nel PDF
**Problema**: CSS non ottimizzato per stampa
**Soluzione**: Il template `preventivo_pdf.html` è specificamente ottimizzato

#### 4. PDF tagliato o contenuto che deborda
**Problema**: Tabelle troppo larghe per la pagina A4
**Soluzione**: Il sistema implementa diverse ottimizzazioni:
- **Larghezze fisse per colonne**: Ogni colonna ha una larghezza percentuale specifica
- **Font ridotti**: Font size ridotto a 11px per il body, 10px per tabelle, 9px per header
- **Layout compatto**: Margini e padding ottimizzati per massimizzare lo spazio
- **Word wrapping**: Testo lungo viene automaticamente spezzato
- **Table layout fixed**: Controlla rigidamente le larghezze delle colonne

**Distribuzione larghezze colonne tabella:**
- Numero riga: 8%
- Descrizione: 42% 
- Quantità: 8%
- Unità: 8%
- Prezzo unitario: 17%
- Totale: 17%

## Struttura File

```
app/
├── services/
│   └── pdf_export_service.py     # Servizio principale PDF
├── templates/
│   └── preventivo/
│       ├── preventivo_documento.html    # Template web
│       └── preventivo_pdf.html          # Template PDF ottimizzato
└── main.py                      # Endpoint API

# File di supporto
setup_weasyprint.sh             # Configurazione ambiente
test_pdf.py                     # Script di test
README_PDF_EXPORT.md            # Questa documentazione
```

## Esempi di Utilizzo

### Da JavaScript (Frontend)
```javascript
// Scarica PDF di preventivo esistente
const downloadPdf = async (preventivoId) => {
    const response = await fetch(`/preventivo/${preventivoId}/pdf?user_id=test-user`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `preventivo_${preventivoId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
};

// Genera PDF da dati attuali
const generatePdf = async (formData) => {
    const response = await fetch('/preventivo/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    });
    // ... gestione download
};
```

### Da Python (Backend)
```python
from app.services.pdf_export_service import PDFExportService
from pathlib import Path

# Inizializza il servizio
pdf_service = PDFExportService(Path("app/templates"))

# Genera PDF
pdf_content = pdf_service.genera_pdf_preventivo(preventivo_data)

# Salva su file
with open("preventivo.pdf", "wb") as f:
    f.write(pdf_content)
```

## Roadmap Future

### Prossime Funzionalità
- [ ] **Template personalizzabili**: Sistema per caricare template aziendali
- [ ] **Watermark**: Opzione per aggiungere filigrane (es. "BOZZA")
- [ ] **Firme digitali**: Integrazione per firme elettroniche
- [ ] **Batch export**: Generazione multipla di PDF
- [ ] **Email integration**: Invio automatico PDF via email

### Ottimizzazioni Tecniche
- [ ] **Cache PDF**: Memorizzazione temporanea dei PDF generati
- [ ] **Background processing**: Generazione asincrona per documenti grandi
- [ ] **Compressione**: Riduzione dimensioni file PDF
- [ ] **Accessibilità**: PDF conformi agli standard PDF/A

## Supporto

Per problemi o domande:
1. Controlla i log dell'applicazione
2. Esegui `python test_pdf.py` per verificare la configurazione
3. Verifica che le dipendenze di sistema siano installate
4. Usa `./setup_weasyprint.sh` per riconfigurare l'ambiente 