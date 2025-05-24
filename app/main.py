from fastapi import FastAPI, Request, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
# from uuid import UUID # Rimuoviamo l'import UUID
from typing import List, Optional

from .models import PreventivoMasterModel, DocumentTemplateCreate, DocumentTemplateUpdate, DocumentTemplateResponse, PreventivoListItem
from .services.preventivo_calculator import calcola_totali_preventivo
from .services.preventivo_service import PreventivoService
from .services.document_template_service import DocumentTemplateService
# Scommento ora che WeasyPrint funziona correttamente
from .services.pdf_export_service import PDFExportService
from .database import get_db, engine, Base
from .db_models import Preventivo

# Modelli Pydantic per la lista preventivi
# Dovrebbero stare in models.py, ma per rapidità li metto qui temporaneamente
from pydantic import BaseModel
from datetime import datetime as dt_datetime # Alias per evitare conflitto
import uuid

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
# Rimuoviamo l'istanza globale, la creeremo on-demand con la sessione DB
# pdf_service = PDFExportService(BASE_DIR / "templates")


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
async def visualizza_preventivo(
    request: Request, 
    preventivo_data: PreventivoMasterModel,
    template_id: Optional[str] = Query(None, description="ID del template da utilizzare"),
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Endpoint per visualizzare un preventivo usando template personalizzabili.
    Accetta un JSON con i dati del preventivo (validato da PreventivoMasterModel),
    calcola i totali e renderizza il template HTML utilizzando il template specificato o quello di default.
    """
    # Calcola i totali e aggiorna preventivo_data in-place
    calcola_totali_preventivo(preventivo_data)

    # Converti il modello Pydantic in un dizionario
    preventivo_dict = preventivo_data.model_dump()
    
    # Se viene specificato un template_id, utilizza quello, altrimenti usa il template di default
    template_service = DocumentTemplateService(db)
    
    if template_id:
        # Recupera il template specifico
        template = template_service.get_template_by_id(template_id, user_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
    else:
        # Utilizza il template di default per l'utente
        template = template_service.get_default_template(user_id, "preventivo")
        if not template:
            # Se non esiste un template di default, creane uno
            template = template_service.create_default_template_for_user(user_id)
    
    # Componi i dati del documento secondo la configurazione del template
    composed_data = template_service.compose_document_from_template(template, preventivo_dict)
    
    return templates.TemplateResponse(
        "preventivo/preventivo_unificato.html", 
        {"request": request, **composed_data}
    )

# Endpoint per salvare un preventivo
@app.post("/preventivo/salva", status_code=status.HTTP_201_CREATED)
async def salva_preventivo_endpoint(
    request: Request, # Rinominato per chiarezza, non più salva_preventivo
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errore nel salvataggio: {str(e)}")

# Endpoint per caricare un preventivo (dati completi per modifica)
@app.get("/preventivo/{preventivo_id}", response_model=PreventivoMasterModel)
async def carica_preventivo_endpoint(
    preventivo_id: str,  # Rinominato per chiarezza
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # UUID dell'utente di test
    db: Session = Depends(get_db)
):
    """
    Carica i dati completi di un preventivo attivo dal database per la modifica.
    """
    preventivo_service = PreventivoService(db)
    # Carica solo preventivi attivi per la modifica
    preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id, solo_attivi=True)
    
    if not preventivo_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo attivo non trovato")
    
    return preventivo_data

# Endpoint per visualizzare un preventivo caricato dal database (HTML)
@app.get("/preventivo/{preventivo_id}/visualizza", response_class=HTMLResponse)
async def visualizza_preventivo_salvato(
    request: Request,
    preventivo_id: str, 
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"), 
    template_id: Optional[str] = Query(None, description="ID del template da utilizzare (opzionale)"),
    db: Session = Depends(get_db)
):
    """
    Carica un preventivo attivo dal database e lo visualizza utilizzando il template specificato o quello di default.
    """
    preventivo_service = PreventivoService(db)
    # Carica solo preventivi attivi per la visualizzazione standard
    preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id, solo_attivi=True)
    
    if not preventivo_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo attivo non trovato")
    
    # Ricalcola i totali (per sicurezza)
    calcola_totali_preventivo(preventivo_data)
    
    # Converti il modello Pydantic in un dizionario
    preventivo_dict = preventivo_data.model_dump()
    
    # Gestione template
    template_service = DocumentTemplateService(db)
    
    if template_id:
        # Utilizza il template specificato
        template = template_service.get_template_by_id(template_id, user_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
    else:
        # Se il preventivo ha un template associato, usalo, altrimenti usa il default
        if preventivo_data.metadati_preventivo and preventivo_data.metadati_preventivo.template_id:
            template_id_from_preventivo = preventivo_data.metadati_preventivo.template_id
            template = template_service.get_template_by_id(template_id_from_preventivo, user_id)
            if not template:
                # Se il template non esiste più, usa il default
                template = template_service.get_default_template(user_id, "preventivo")
                if not template:
                    template = template_service.create_default_template_for_user(user_id)
        else:
            # Utilizza il template di default
            template = template_service.get_default_template(user_id, "preventivo")
            if not template:
                template = template_service.create_default_template_for_user(user_id)
    
    # Componi i dati del documento secondo la configurazione del template
    composed_data = template_service.compose_document_from_template(template, preventivo_dict)

    return templates.TemplateResponse(
        "preventivo/preventivo_unificato.html", 
        {"request": request, **composed_data}
    )

# Endpoint per elencare i preventivi ATTIVI di un utente
@app.get("/preventivi/attivi", response_model=List[PreventivoListItem])
async def lista_preventivi_attivi_endpoint(
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Restituisce la lista dei preventivi ATTIVI per un utente con paginazione.
    """
    preventivo_service = PreventivoService(db)
    preventivi_attivi = preventivo_service.lista_preventivi_attivi(user_id, skip, limit)
    return preventivi_attivi # Pydantic si occuperà della serializzazione

# Endpoint per elencare i preventivi CESTINATI di un utente
@app.get("/preventivi/cestinati", response_model=List[PreventivoListItem])
async def lista_preventivi_cestinati_endpoint(
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Restituisce la lista dei preventivi CESTINATI per un utente con paginazione.
    """
    preventivo_service = PreventivoService(db)
    preventivi_cestinati = preventivo_service.lista_preventivi_cestinati(user_id, skip, limit)
    return preventivi_cestinati

# Endpoint per CESTINARE un preventivo (soft delete)
@app.post("/preventivo/{preventivo_id}/cestina", status_code=status.HTTP_200_OK)
async def cestina_preventivo_endpoint(
    preventivo_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    preventivo_service = PreventivoService(db)
    preventivo_cestinato = preventivo_service.cestina_preventivo(preventivo_id, user_id)
    if not preventivo_cestinato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo attivo non trovato o già cestinato")
    return {"message": "Preventivo spostato nel cestino", "preventivo_id": preventivo_id, "stato_record": "cestinato"}

# Endpoint per RIPRISTINARE un preventivo dal cestino
@app.post("/preventivo/{preventivo_id}/ripristina", status_code=status.HTTP_200_OK)
async def ripristina_preventivo_endpoint(
    preventivo_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    preventivo_service = PreventivoService(db)
    preventivo_ripristinato = preventivo_service.ripristina_preventivo(preventivo_id, user_id)
    if not preventivo_ripristinato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo non trovato nel cestino o errore nel ripristino")
    return {"message": "Preventivo ripristinato con successo", "preventivo_id": preventivo_id, "stato_record": "attivo"}

# Endpoint per ELIMINARE DEFINITIVAMENTE un preventivo
@app.delete("/preventivo/{preventivo_id}/definitivo", status_code=status.HTTP_200_OK)
async def elimina_definitivamente_preventivo_endpoint(
    preventivo_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    preventivo_service = PreventivoService(db)
    success = preventivo_service.elimina_definitivamente_preventivo(preventivo_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo non trovato")
    return {"message": "Preventivo eliminato definitivamente", "preventivo_id": preventivo_id}

# Endpoint per SVUOTARE IL CESTINO dei preventivi scaduti per l'utente
@app.post("/preventivi/cestino/svuota_scaduti", status_code=status.HTTP_200_OK)
async def svuota_cestino_utente_endpoint(
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    giorni_scadenza: int = Query(30, description="Numero di giorni dopo i quali un preventivo cestinato è considerato scaduto"),
    db: Session = Depends(get_db)
):
    preventivo_service = PreventivoService(db)
    num_eliminati = preventivo_service.svuota_cestino_scaduti(user_id=user_id, giorni_scadenza=giorni_scadenza)
    return {"message": f"{num_eliminati} preventivi scaduti eliminati dal cestino.", "count": num_eliminati}

# Endpoint per SVUOTARE TUTTO IL CESTINO per l'utente
@app.post("/preventivi/cestino/svuota_tutto", status_code=status.HTTP_200_OK)
async def svuota_tutto_cestino_utente_endpoint(
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    preventivo_service = PreventivoService(db)
    num_eliminati = preventivo_service.svuota_tutto_cestino(user_id=user_id)
    return {"message": f"{num_eliminati} preventivi eliminati definitivamente dal cestino.", "count": num_eliminati}

# Il vecchio endpoint /preventivi è stato sostituito da /preventivi/attivi e /preventivi/cestinati
# @app.get("/preventivi") ... -> Rimosso o da aggiornare se si vuole un comportamento diverso

# Endpoint per export PDF da dati POST
@app.post("/preventivo/pdf", response_class=Response)
async def genera_pdf_preventivo(preventivo_data: PreventivoMasterModel, db: Session = Depends(get_db)):
    """
    Genera un PDF del preventivo a partire dai dati forniti.
    Accetta un JSON con i dati del preventivo e restituisce il PDF.
    Utilizza il template di default dell'utente.
    """
    try:
        # Istanzia PDFExportService con la sessione DB
        pdf_service_local = PDFExportService(BASE_DIR / "templates", db=db)
        template_service = DocumentTemplateService(db)
        
        # TODO: Ottenere user_id dai dati del preventivo o da un token JWT
        # Per ora usiamo l'user_id di default.
        user_id_per_default_template = "da2cb935-e023-40dd-9703-d918f1066b24" 
        default_template = template_service.get_default_template(user_id_per_default_template, "preventivo")
        if not default_template:
            default_template = template_service.create_default_template_for_user(user_id_per_default_template)

        # Genera il PDF usando il servizio con il template di default
        pdf_content = pdf_service_local.genera_pdf_preventivo_con_template(preventivo_data, default_template)
        
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore nella generazione del PDF: {str(e)}")

# Endpoint per export PDF di un preventivo salvato
@app.get("/preventivo/{preventivo_id}/pdf", response_class=Response)
async def scarica_pdf_preventivo(
    preventivo_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),  # Aggiorno con UUID reale
    template_id: Optional[str] = Query(None, description="ID del template da utilizzare (opzionale)"),
    db: Session = Depends(get_db)
):
    """
    Scarica il PDF di un preventivo salvato nel database.
    """
    try:
        # Carica il preventivo dal database (solo attivi di default)
        preventivo_service = PreventivoService(db)
        preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id, solo_attivi=True)
        
        if not preventivo_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preventivo attivo non trovato")
        
        # Istanzia PDFExportService con la sessione DB
        pdf_service_local = PDFExportService(BASE_DIR / "templates", db=db)
        template_service = DocumentTemplateService(db)
        
        if template_id:
            # Utilizza il template specificato nel parametro
            template = template_service.get_template_by_id(template_id, user_id)
            if not template:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
        else:
            # Se il preventivo ha un template associato, usalo, altrimenti usa il default
            if preventivo_data.metadati_preventivo and preventivo_data.metadati_preventivo.template_id:
                template_id_from_preventivo = preventivo_data.metadati_preventivo.template_id
                template = template_service.get_template_by_id(template_id_from_preventivo, user_id)
                if not template:
                    # Se il template non esiste più, usa il default
                    template = template_service.get_default_template(user_id, "preventivo")
                    if not template:
                        template = template_service.create_default_template_for_user(user_id)
            else:
                # Utilizza il template di default
                template = template_service.get_default_template(user_id, "preventivo")
                if not template:
                    template = template_service.create_default_template_for_user(user_id)
        
        # Genera il PDF usando il template corretto
        pdf_content = pdf_service_local.genera_pdf_preventivo_con_template(preventivo_data, template)
        
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore nella generazione del PDF: {str(e)}")

# ============================================
# ENDPOINTS TEMPLATE DOCUMENTI
# ============================================

@app.get("/templates/composer", response_class=HTMLResponse)
async def template_composer(request: Request):
    """
    Pagina per la creazione e modifica di template documenti.
    """
    return templates.TemplateResponse("template_composer.html", {"request": request})

@app.get("/templates", response_model=List[DocumentTemplateResponse]) # Aggiornato response_model
async def lista_template_utente(
    document_type: Optional[str] = Query(None, description="Filtra per tipo documento"),
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Restituisce la lista dei template dell'utente
    """
    template_service = DocumentTemplateService(db)
    templates_db = template_service.get_user_templates(user_id, document_type)
    
    # Converte in formato JSON-serializable usando il modello Pydantic DocumentTemplateResponse
    return [DocumentTemplateResponse.from_orm(t) for t in templates_db] # from_orm è per Pydantic V1
    # Per Pydantic V2: return [DocumentTemplateResponse.model_validate(t) for t in templates_db]

@app.post("/templates", response_class=JSONResponse, status_code=status.HTTP_201_CREATED)
async def crea_template(
    template_data: DocumentTemplateCreate,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo template documento
    """
    template_service = DocumentTemplateService(db)
    
    # Valida la composizione dei moduli
    validation_result = template_service.validate_module_composition(template_data.module_composition)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "message": "Composizione moduli non valida",
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }
        )
    
    try:
        db_template = template_service.create_template(user_id, template_data)
        
        return {
            "message": "Template creato con successo",
            "template_id": str(db_template.id),
            "warnings": validation_result["warnings"]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errore nella creazione del template: {str(e)}")

@app.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def ottieni_template(
    template_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Recupera un template specifico
    """
    template_service = DocumentTemplateService(db)
    template = template_service.get_template_by_id(template_id, user_id)
    
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
    
    return DocumentTemplateResponse.from_orm(template) # from_orm per Pydantic V1
    # Per Pydantic V2: return DocumentTemplateResponse.model_validate(template)

@app.put("/templates/{template_id}", response_class=JSONResponse)
async def aggiorna_template(
    template_id: str,
    template_data: DocumentTemplateUpdate,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un template esistente
    """
    template_service = DocumentTemplateService(db)
    
    # Valida la composizione dei moduli se presente
    if template_data.module_composition:
        validation_result = template_service.validate_module_composition(template_data.module_composition)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={
                    "message": "Composizione moduli non valida",
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"]
                }
            )
    
    try:
        updated_template = template_service.update_template(template_id, user_id, template_data)
        
        if not updated_template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
        
        return {
            "message": "Template aggiornato con successo",
            "template_id": str(updated_template.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errore nell'aggiornamento del template: {str(e)}")

@app.delete("/templates/{template_id}", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def elimina_template(
    template_id: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Elimina un template
    """
    template_service = DocumentTemplateService(db)
    
    success = template_service.delete_template(template_id, user_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template non trovato")
    
    return {"message": "Template eliminato con successo"}

@app.get("/templates/default/{document_type}", response_model=DocumentTemplateResponse) # Aggiornato response_model
async def ottieni_template_default(
    document_type: str,
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Recupera il template di default per un tipo di documento
    """
    template_service = DocumentTemplateService(db)
    template = template_service.get_default_template(user_id, document_type)
    
    if not template:
        # Se non esiste un template default, crea uno di default
        template = template_service.create_default_template_for_user(user_id)
    
    return DocumentTemplateResponse.from_orm(template) # from_orm per Pydantic V1
    # Per Pydantic V2: return DocumentTemplateResponse.model_validate(template)

@app.post("/templates/validate", response_class=JSONResponse)
async def valida_composizione_moduli(
    module_composition: dict,
    db: Session = Depends(get_db)
):
    """
    Valida una composizione di moduli senza creare il template
    """
    template_service = DocumentTemplateService(db)
    
    try:
        from .models import ModuleComposition
        composition = ModuleComposition(**module_composition)
        validation_result = template_service.validate_module_composition(composition)
        
        return validation_result
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Errore nella validazione: {str(e)}"],
            "warnings": []
        }

@app.post("/preventivo/preview", response_class=HTMLResponse)
async def anteprima_preventivo_con_template(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint per generare anteprima di un preventivo con configurazione template personalizzata.
    Utilizzato dal Template Composer per mostrare l'anteprima in tempo reale.
    
    Accetta nel body:
    - preventivo_data: dati del preventivo (PreventivoMasterModel)
    - template_config: configurazione del template (non salvato)
    """
    try:
        # Leggi il body della richiesta
        body = await request.json()
        
        # Estrai i dati del preventivo e la configurazione del template
        preventivo_data = PreventivoMasterModel(**body["preventivo_data"])
        template_config = body["template_config"]
        
        # Calcola i totali
        calcola_totali_preventivo(preventivo_data)
        
        # Converti il modello Pydantic in un dizionario
        preventivo_dict = preventivo_data.model_dump()
        
        # Usa il DocumentTemplateService per comporre i dati usando la configurazione fornita
        template_service = DocumentTemplateService(db)
        
        # Crea un oggetto template-like dalla configurazione
        # from .models import ModuleComposition, DocumentTemplateResponse # ModuleComposition non serve qui
        # from datetime import datetime # Non serve qui
        
        # Simula un template con la configurazione fornita
        mock_template = type('MockTemplate', (), {
            'id': 'preview',
            'name': template_config.get('name', 'Preview Template'),
            'description': template_config.get('description', ''),
            'document_type': template_config.get('document_type', 'preventivo'),
            'module_composition': template_config.get('module_composition', {"modules": []}),
            'page_format': template_config.get('page_format', 'A4'),
            'page_orientation': template_config.get('page_orientation', 'portrait'),
            'margins': template_config.get('margins', {"top": 1.2, "bottom": 1.2, "left": 0.8, "right": 0.8}),
            'custom_styles': template_config.get('custom_styles', ''),
            'is_default': False,
            'is_public': False,
            'version': 1
        })()
        
        # Componi i dati del documento secondo la configurazione del template
        composed_data = template_service.compose_document_from_template(mock_template, preventivo_dict)
        
        return templates.TemplateResponse(
            "preventivo/preventivo_unificato.html", 
            {"request": request, **composed_data}
        )
        
    except Exception as e:
        # In caso di errore, restituisci un HTML con l'errore
        error_html = f"""
        <div class="p-4 bg-red-50 border border-red-200 rounded-md">
            <h3 class="text-red-800 font-medium">Errore nell'anteprima</h3>
            <p class="text-red-600 text-sm mt-1">{str(e)}</p>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=status.HTTP_400_BAD_REQUEST)

# Esempio di come potresti avviare l'app con Uvicorn da riga di comando:
# uvicorn app.main:app --reload
# (assicurati di essere nella directory principale del progetto, non dentro 'app/') 