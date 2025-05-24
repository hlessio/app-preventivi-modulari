from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ..db_models import DocumentTemplate, User, UserPreferences
from ..models import (
    DocumentTemplateCreate, 
    DocumentTemplateUpdate, 
    DocumentTemplateResponse,
    ModuleComposition,
    ModuleConfig
)

class DocumentTemplateService:
    """Servizio per gestire template documenti personalizzabili"""
    
    # Mappatura dei moduli JSON master ai nomi dei moduli template
    MODULE_MAPPING = {
        "azienda_emittente": "intestazione_azienda",
        "metadati_preventivo": "metadati_preventivo",
        "cliente_destinatario": "intestazione_cliente", 
        "corpo_preventivo": "tabella_preventivo",
        "dettagli_totali": "sezione_totali",
        "condizioni_contrattuali": "condizioni_generali",
        "elementi_footer": "footer_preventivo"
    }
    
    # Template di default che replica il comportamento attuale
    DEFAULT_TEMPLATE_COMPOSITION = {
        "modules": [
            {
                "module_name": "intestazione_azienda",
                "order": 1,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "metadati_preventivo", 
                "order": 2,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "intestazione_cliente",
                "order": 3, 
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "tabella_preventivo",
                "order": 4,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "sezione_totali",
                "order": 5,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "condizioni_generali",
                "order": 6,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "footer_preventivo",
                "order": 7,
                "enabled": True,
                "custom_config": {}
            }
        ]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, user_id: str, template_data: DocumentTemplateCreate) -> DocumentTemplate:
        """Crea un nuovo template documento"""
        
        # Se questo è impostato come default, rimuovi il flag da altri template
        if template_data.is_default:
            self._clear_user_default_templates(user_id, template_data.document_type)
        
        # Crea il nuovo template
        db_template = DocumentTemplate(
            user_id=user_id,
            name=template_data.name,
            description=template_data.description,
            document_type=template_data.document_type,
            module_composition=template_data.module_composition.model_dump(),
            page_format=template_data.page_format,
            page_orientation=template_data.page_orientation,
            margins=template_data.margins,
            custom_styles=template_data.custom_styles,
            is_default=template_data.is_default,
            is_public=template_data.is_public
        )
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def get_user_templates(self, user_id: str, document_type: Optional[str] = None) -> List[DocumentTemplate]:
        """Recupera template utente, opzionalmente filtrati per tipo documento"""
        query = self.db.query(DocumentTemplate).filter(DocumentTemplate.user_id == user_id)
        
        if document_type:
            query = query.filter(DocumentTemplate.document_type == document_type)
            
        return query.order_by(DocumentTemplate.is_default.desc(), DocumentTemplate.created_at.desc()).all()
    
    def get_template_by_id(self, template_id: str, user_id: str) -> Optional[DocumentTemplate]:
        """Recupera un template specifico dell'utente"""
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.id == template_id,
            DocumentTemplate.user_id == user_id
        ).first()
    
    def update_template(self, template_id: str, user_id: str, update_data: DocumentTemplateUpdate) -> Optional[DocumentTemplate]:
        """Aggiorna un template esistente"""
        db_template = self.get_template_by_id(template_id, user_id)
        if not db_template:
            return None
        
        # Se viene impostato come default, rimuovi il flag da altri template
        if update_data.is_default is True:
            self._clear_user_default_templates(user_id, db_template.document_type)
        
        # Aggiorna i campi forniti
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Gestione speciale per module_composition
        if "module_composition" in update_dict:
            update_dict["module_composition"] = update_dict["module_composition"].model_dump() if update_dict["module_composition"] else None
        
        for field, value in update_dict.items():
            setattr(db_template, field, value)
        
        db_template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def delete_template(self, template_id: str, user_id: str) -> bool:
        """Elimina un template"""
        db_template = self.get_template_by_id(template_id, user_id)
        if not db_template:
            return False
        
        # Non permettere di eliminare template se è in uso da documenti
        # (questa logica può essere estesa in futuro)
        
        self.db.delete(db_template)
        self.db.commit()
        
        return True
    
    def get_default_template(self, user_id: str, document_type: str = "preventivo") -> Optional[DocumentTemplate]:
        """Recupera il template di default per un tipo di documento"""
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.user_id == user_id,
            DocumentTemplate.document_type == document_type,
            DocumentTemplate.is_default == True
        ).first()
    
    def create_default_template_for_user(self, user_id: str) -> DocumentTemplate:
        """Crea il template di default per un nuovo utente"""
        default_template = DocumentTemplateCreate(
            name="Preventivo Standard A4 Verticale",
            description="Template di default che replica il comportamento standard del sistema",
            document_type="preventivo", 
            module_composition=ModuleComposition(**self.DEFAULT_TEMPLATE_COMPOSITION),
            page_format="A4",
            page_orientation="portrait",
            margins={"top": 1.2, "right": 0.8, "bottom": 1.2, "left": 0.8},
            is_default=True,
            is_public=False
        )
        
        return self.create_template(user_id, default_template)
    
    def compose_document_from_template(self, template: DocumentTemplate, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera la struttura dati per renderizzare un documento usando un template specifico.
        
        Questa funzione prende:
        - Un template con la configurazione dei moduli
        - I dati del documento (JSON master)
        
        E ritorna:
        - I dati organizzati secondo il template per il rendering
        """
        
        # Estrai la configurazione moduli dal template
        modules_config = template.module_composition.get("modules", [])
        
        # Ordina i moduli per order
        sorted_modules = sorted(modules_config, key=lambda x: x.get("order", 999))
        
        # Filtra solo i moduli abilitati
        enabled_modules = [m for m in sorted_modules if m.get("enabled", True)]
        
        # Costruisci la struttura dati per il rendering
        composed_data = {
            "template_config": {
                "name": template.name,
                "document_type": template.document_type,
                "page_format": template.page_format,
                "page_orientation": template.page_orientation,
                "margins": template.margins,
                "custom_styles": template.custom_styles
            },
            "modules_order": enabled_modules,
            "document_data": document_data
        }
        
        return composed_data
    
    def validate_module_composition(self, composition: ModuleComposition) -> Dict[str, Any]:
        """Valida che tutti i moduli referenziati esistano e la configurazione sia valida"""
        
        errors = []
        warnings = []
        
        module_names = [m.module_name for m in composition.modules]
        orders = [m.order for m in composition.modules]
        
        # Controlla duplicati nei nomi dei moduli
        if len(module_names) != len(set(module_names)):
            errors.append("Nomi dei moduli duplicati trovati")
        
        # Controlla duplicati negli ordini
        if len(orders) != len(set(orders)):
            errors.append("Numeri di ordine duplicati trovati")
        
        # Controlla che i moduli esistano (per ora solo i built-in)
        valid_modules = set(self.MODULE_MAPPING.values())
        for module_name in module_names:
            if module_name not in valid_modules:
                warnings.append(f"Modulo '{module_name}' non riconosciuto come built-in")
        
        # Controlla che almeno un modulo sia abilitato
        enabled_modules = [m for m in composition.modules if m.enabled]
        if not enabled_modules:
            errors.append("Almeno un modulo deve essere abilitato")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _clear_user_default_templates(self, user_id: str, document_type: str):
        """Rimuove il flag default da tutti i template dell'utente per un tipo documento"""
        self.db.query(DocumentTemplate).filter(
            DocumentTemplate.user_id == user_id,
            DocumentTemplate.document_type == document_type,
            DocumentTemplate.is_default == True
        ).update({DocumentTemplate.is_default: False})
        
        self.db.commit()
    
    def _convert_template_for_response(self, template: DocumentTemplate) -> DocumentTemplate:
        """Converte un template dal database per renderlo compatibile con DocumentTemplateResponse"""
        
        # Converti module_composition da dict a ModuleComposition se necessario
        if isinstance(template.module_composition, dict):
            try:
                # Crea gli oggetti ModuleConfig dalla lista di dizionari
                modules = []
                for module_dict in template.module_composition.get("modules", []):
                    modules.append(ModuleConfig(**module_dict))
                
                # Crea l'oggetto ModuleComposition
                template.module_composition = ModuleComposition(modules=modules)
            except Exception as e:
                print(f"Errore nella conversione di module_composition per template {template.id}: {e}")
                # Fallback: crea una composizione vuota
                template.module_composition = ModuleComposition(modules=[])
        
        return template 