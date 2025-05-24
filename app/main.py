from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
# from uuid import UUID # Rimuoviamo l'import UUID
from typing import List, Optional

from .models import PreventivoMasterModel, DocumentTemplateCreate, DocumentTemplateUpdate, DocumentTemplateResponse
from .services.preventivo_calculator import calcola_totali_preventivo
from .services.preventivo_service import PreventivoService
from .services.document_template_service import DocumentTemplateService
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
            raise HTTPException(status_code=404, detail="Template non trovato")
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
    template_id: Optional[str] = Query(None, description="ID del template da utilizzare (opzionale)"),
    db: Session = Depends(get_db)
):
    """
    Carica un preventivo dal database e lo visualizza utilizzando il template specificato o quello di default.
    """
    preventivo_service = PreventivoService(db)
    preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id)
    
    if not preventivo_data:
        raise HTTPException(status_code=404, detail="Preventivo non trovato")
    
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
            raise HTTPException(status_code=404, detail="Template non trovato")
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
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

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
        # Carica il preventivo dal database
        preventivo_service = PreventivoService(db)
        preventivo_data = preventivo_service.carica_preventivo(preventivo_id, user_id)
        
        if not preventivo_data:
            raise HTTPException(status_code=404, detail="Preventivo non trovato")
        
        # Istanzia PDFExportService con la sessione DB
        pdf_service_local = PDFExportService(BASE_DIR / "templates", db=db)
        template_service = DocumentTemplateService(db)
        
        if template_id:
            # Utilizza il template specificato nel parametro
            template = template_service.get_template_by_id(template_id, user_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template non trovato")
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
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

# ============================================
# ENDPOINTS TEMPLATE DOCUMENTI
# ============================================

@app.get("/templates/composer", response_class=HTMLResponse)
async def template_composer(request: Request):
    """
    Pagina per la creazione e modifica di template documenti.
    """
    return templates.TemplateResponse("template_composer.html", {"request": request})

@app.get("/templates", response_class=JSONResponse)
async def lista_template_utente(
    document_type: Optional[str] = Query(None, description="Filtra per tipo documento"),
    user_id: str = Query(default="da2cb935-e023-40dd-9703-d918f1066b24", description="ID dell'utente"),
    db: Session = Depends(get_db)
):
    """
    Restituisce la lista dei template dell'utente
    """
    template_service = DocumentTemplateService(db)
    templates = template_service.get_user_templates(user_id, document_type)
    
    # Converte in formato JSON-serializable
    templates_json = []
    for template in templates:
        templates_json.append({
            "id": str(template.id),
            "name": template.name,
            "description": template.description,
            "document_type": template.document_type,
            "module_composition": template.module_composition,
            "page_format": template.page_format,
            "page_orientation": template.page_orientation,
            "margins": template.margins,
            "is_default": template.is_default,
            "is_public": template.is_public,
            "version": template.version,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        })
    
    return {"templates": templates_json}

@app.post("/templates", response_class=JSONResponse)
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
            status_code=400, 
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
        raise HTTPException(status_code=400, detail=f"Errore nella creazione del template: {str(e)}")

@app.get("/templates/{template_id}", response_class=JSONResponse)
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
        raise HTTPException(status_code=404, detail="Template non trovato")
    
    return {
        "id": str(template.id),
        "user_id": str(template.user_id),
        "name": template.name,
        "description": template.description,
        "document_type": template.document_type,
        "module_composition": template.module_composition,
        "page_format": template.page_format,
        "page_orientation": template.page_orientation,
        "margins": template.margins,
        "custom_styles": template.custom_styles,
        "is_default": template.is_default,
        "is_public": template.is_public,
        "version": template.version,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat()
    }

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
                status_code=400, 
                detail={
                    "message": "Composizione moduli non valida",
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"]
                }
            )
    
    try:
        updated_template = template_service.update_template(template_id, user_id, template_data)
        
        if not updated_template:
            raise HTTPException(status_code=404, detail="Template non trovato")
        
        return {
            "message": "Template aggiornato con successo",
            "template_id": str(updated_template.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore nell'aggiornamento del template: {str(e)}")

@app.delete("/templates/{template_id}", response_class=JSONResponse)
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
        raise HTTPException(status_code=404, detail="Template non trovato")
    
    return {"message": "Template eliminato con successo"}

@app.get("/templates/default/{document_type}", response_class=JSONResponse)
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
    
    return {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "document_type": template.document_type,
        "module_composition": template.module_composition,
        "page_format": template.page_format,
        "page_orientation": template.page_orientation,
        "margins": template.margins,
        "is_default": template.is_default
    }

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
        from .models import ModuleComposition, DocumentTemplateResponse
        from datetime import datetime
        
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
        return HTMLResponse(content=error_html, status_code=400)

# Esempio di come potresti avviare l'app con Uvicorn da riga di comando:
# uvicorn app.main:app --reload
# (assicurati di essere nella directory principale del progetto, non dentro 'app/') 