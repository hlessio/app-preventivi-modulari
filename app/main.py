from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
# from uuid import UUID # Rimuoviamo l'import UUID
from typing import List

from .models import PreventivoMasterModel
from .services.preventivo_calculator import calcola_totali_preventivo
from .services.preventivo_service import PreventivoService
# Scommento ora che WeasyPrint funziona correttamente
from .services.pdf_export_service import PDFExportService
from .database import get_db, engine, Base
from .db_models import Preventivo

# Crea le tabelle nel database (per ora facciamo così, in futuro useremo Alembic)
# Commento perché ora usiamo Alembic per le migrazioni
# Base.metadata.create_all(bind=engine)

# Definisci il percorso base del progetto o dell'app
# Questo è utile per trovare la directory dei template in modo robusto
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="App Preventivi Modulari")

# Configurazione dei template Jinja2
# Assicurati che la directory 'templates' sia al livello corretto rispetto a BASE_DIR
# In questo caso, se main.py è in app/, e templates è in app/templates/
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configurazione del servizio PDF - Ora abilitato
pdf_service = PDFExportService(BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Dashboard principale con lista preventivi
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/test_simple", response_class=HTMLResponse)
async def test_simple(request: Request):
    """
    Pagina di test semplificata per debug interazioni
    """
    return templates.TemplateResponse("test_simple.html", {"request": request})


@app.get("/preventivo/nuovo", response_class=HTMLResponse)
async def nuovo_preventivo(request: Request):
    """
    Form per creare un nuovo preventivo
    """
    return templates.TemplateResponse("preventivo_form.html", {
        "request": request,
        "preventivo_id": None
    })


@app.get("/preventivo/{preventivo_id}/modifica", response_class=HTMLResponse)
async def modifica_preventivo(request: Request, preventivo_id: str):
    """
    Form per modificare un preventivo esistente
    """
    return templates.TemplateResponse("preventivo_form.html", {
        "request": request,
        "preventivo_id": preventivo_id
    })


@app.post("/preventivo/visualizza", response_class=HTMLResponse)
async def visualizza_preventivo(request: Request, preventivo_data: PreventivoMasterModel):
    """
    Endpoint per visualizzare un preventivo usando il template unificato.
    Accetta un JSON con i dati del preventivo (validato da PreventivoMasterModel),
    calcola i totali e renderizza il template HTML.
    """
    # Calcola i totali e aggiorna preventivo_data in-place
    calcola_totali_preventivo(preventivo_data)

    # Convertiamo il modello Pydantic (ora aggiornato con i totali) in un dizionario
    preventivo_dict = preventivo_data.model_dump()

    return templates.TemplateResponse(
        "preventivo/preventivo_unificato.html", 
        {"request": request, **preventivo_dict}
    )

# Endpoint per salvare un preventivo
@app.post("/preventivo/salva")
async def salva_preventivo(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Salva un nuovo preventivo nel database.
    Accetta i dati in formato JSON nel body della richiesta.
    """
    try:
        # Leggi il body della richiesta
        body = await request.json()
        
        # Estrai user_id dai dati - Uso UUID reale dell'utente di test
        user_id = body.pop("user_id", "da2cb935-e023-40dd-9703-d918f1066b24")  # UUID dell'utente di test
        
        # Valida i dati con Pydantic
        preventivo_data = PreventivoMasterModel(**body)
        
        # Calcola i totali prima di salvare
        calcola_totali_preventivo(preventivo_data)
        
        # Utilizza il servizio per salvare il preventivo
        preventivo_service = PreventivoService(db)
        db_preventivo = preventivo_service.salva_preventivo(preventivo_data, user_id)
        
        return {
            "message": "Preventivo salvato con successo",
            "preventivo_id": str(db_preventivo.id),
            "numero_preventivo": db_preventivo.numero_preventivo
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore nel salvataggio: {str(e)}")

# Endpoint per caricare un preventivo
@app.get("/preventivo/{preventivo_id}")
async def carica_preventivo(
    preventivo_id: str,  # Cambiato da UUID a str
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # UUID dell'utente di test
    db: Session = Depends(get_db)
):
    """
    Carica un preventivo dal database.
    """
    preventivo_service = PreventivoService(db)
    preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id)
    
    if not preventivo_data:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    
    return preventivo_data

# Endpoint per visualizzare un preventivo caricato dal database
@app.get("/preventivo/{preventivo_id}/visualizza", response_class=HTMLResponse)
async def visualizza_preventivo_salvato(
    request: Request,
    preventivo_id: str,  # Cambiato da UUID a str
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # UUID dell'utente di test
    db: Session = Depends(get_db)
):
    """
    Carica un preventivo dal database e lo visualizza.
    """
    preventivo_service = PreventivoService(db)
    preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id)
    
    if not preventivo_data:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    
    # Ricalcola i totali (per sicurezza)
    calcola_totali_preventivo(preventivo_data)
    
    # Convertiamo il modello Pydantic in un dizionario
    preventivo_dict = preventivo_data.model_dump()

    return templates.TemplateResponse(
        "preventivo/preventivo_unificato.html", 
        {"request": request, **preventivo_dict}
    )

# Endpoint per elencare i preventivi di un utente
@app.get("/preventivi")
async def lista_preventivi(
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # UUID dell'utente di test
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Restituisce la lista dei preventivi per un utente.
    """
    preventivo_service = PreventivoService(db)
    preventivi = preventivo_service.lista_preventivi(user_id, skip, limit)
    
    # Converte la lista in un formato JSON-serializable
    preventivi_json = []
    for p in preventivi:
        preventivi_json.append({
            "id": str(p.id),
            "numero_preventivo": p.numero_preventivo,
            "oggetto_preventivo": p.oggetto_preventivo,
            "stato_preventivo": p.stato_preventivo,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        })
    
    return {"preventivi": preventivi_json}

# Endpoint per export PDF da dati POST
@app.post("/preventivo/pdf", response_class=Response)
async def genera_pdf_preventivo(preventivo_data: PreventivoMasterModel):
    """
    Genera un PDF del preventivo a partire dai dati forniti.
    Accetta un JSON con i dati del preventivo e restituisce il PDF.
    """
    try:
        # Genera il PDF usando il servizio
        pdf_content = pdf_service.genera_pdf_preventivo(preventivo_data)
        
        # Crea il nome del file PDF
        numero_preventivo = preventivo_data.metadati_preventivo.numero_preventivo or "preventivo"
        filename = f"preventivo_{numero_preventivo}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

# Endpoint per export PDF di un preventivo salvato
@app.get("/preventivo/{preventivo_id}/pdf", response_class=Response)
async def scarica_pdf_preventivo(
    preventivo_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # Aggiorno con UUID reale
    db: Session = Depends(get_db)
):
    """
    Scarica il PDF di un preventivo salvato nel database.
    """
    try:
        # Carica il preventivo dal database
        preventivo_service = PreventivoService(db)
        preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id)
        
        if not preventivo_data:
            raise HTTPException(status_code=404, detail="Preventivo non trovato")
        
        # Genera il PDF
        pdf_content = pdf_service.genera_pdf_preventivo(preventivo_data)
        
        # Crea il nome del file PDF
        numero_preventivo = preventivo_data.metadati_preventivo.numero_preventivo or preventivo_id
        filename = f"preventivo_{numero_preventivo}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

# Esempio di come potresti avviare l'app con Uvicorn da riga di comando:
# uvicorn app.main:app --reload
# (assicurati di essere nella directory principale del progetto, non dentro 'app/') 