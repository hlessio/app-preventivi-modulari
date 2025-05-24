from pathlib import Path
import logging
from typing import Optional, Union
from jinja2 import Environment, FileSystemLoader
import tempfile

# Setup logger
logger = logging.getLogger(__name__)

# Tentativo di importare WeasyPrint
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
    logger.info("✅ WeasyPrint caricato correttamente")
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    logger.warning(f"⚠️ WeasyPrint non disponibile: {e}")
    # Definiamo delle classi mock per evitare errori di tipo
    HTML = None
    CSS = None
except Exception as e:
    WEASYPRINT_AVAILABLE = False
    logger.error(f"❌ Errore nel caricamento WeasyPrint: {e}")
    HTML = None
    CSS = None

from ..models import PreventivoMasterModel
from ..services.preventivo_calculator import calcola_totali_preventivo


class PDFExportService:
    """
    Servizio per l'export PDF dei preventivi con fallback graceful.
    Se WeasyPrint non è disponibile, fornisce messaggi di errore utili.
    """
    
    def __init__(self, templates_dir: Path):
        """
        Inizializza il servizio con la directory dei template
        
        Args:
            templates_dir: Path alla directory contenente i template Jinja2
        """
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))
        self.is_available = WEASYPRINT_AVAILABLE
        
        if not self.is_available:
            logger.warning("🔧 PDFExportService inizializzato senza WeasyPrint - funzionalità PDF disabilitate")
        
    def genera_pdf_preventivo(self, preventivo_data: PreventivoMasterModel) -> bytes:
        """
        Genera un PDF del preventivo usando il template unificato.
        
        Args:
            preventivo_data: Dati del preventivo validati
            
        Returns:
            bytes: Contenuto del PDF
            
        Raises:
            RuntimeError: Se WeasyPrint non è disponibile
            Exception: Altri errori di generazione PDF
        """
        if not self.is_available:
            raise RuntimeError(
                "❌ Export PDF non disponibile. "
                "WeasyPrint non è installato correttamente. "
                "Consulta la documentazione per l'installazione delle dipendenze di sistema."
            )
        
        try:
            # Assicuriamoci che i totali siano calcolati
            calcola_totali_preventivo(preventivo_data)
            
            # Renderizza l'HTML usando il template unificato
            html_content = self._renderizza_html_pdf(preventivo_data)
            
            # Genera il PDF usando SOLO l'HTML (il CSS è incorporato nel template)
            pdf_bytes = self._genera_pdf_da_html(html_content)
            
            logger.info(f"✅ PDF generato con successo per preventivo {preventivo_data.metadati_preventivo.numero_preventivo}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ Errore nella generazione PDF: {e}")
            raise Exception(f"Errore nella generazione del PDF: {str(e)}")
    
    def _renderizza_html_pdf(self, preventivo_data: PreventivoMasterModel) -> str:
        """
        Renderizza l'HTML del preventivo usando il template unificato
        
        Args:
            preventivo_data: Dati del preventivo
            
        Returns:
            str: HTML renderizzato
        """
        # Usa il template unificato che gestisce sia web che PDF
        template_name = "preventivo/preventivo_unificato.html"
        
        try:
            template = self.env.get_template(template_name)
        except:
            # Fallback ai template esistenti se l'unificato non esiste
            try:
                template = self.env.get_template("preventivo/preventivo_pdf.html")
            except:
                template = self.env.get_template("preventivo/preventivo_documento.html")
        
        # Converti il modello Pydantic in dizionario
        context = preventivo_data.model_dump()
        
        # Renderizza l'HTML
        return template.render(**context)
    
    def _genera_pdf_da_html(self, html_content: str) -> bytes:
        """
        Converte l'HTML in PDF usando WeasyPrint
        
        Args:
            html_content: Contenuto HTML da convertire
            
        Returns:
            bytes: PDF generato
        """
        # Crea il documento HTML
        html_doc = HTML(string=html_content)
        
        # Genera il PDF
        pdf_bytes = html_doc.write_pdf()
        
        return pdf_bytes
    
    def _get_pdf_css(self) -> Optional[str]:
        """
        [OBSOLETO] CSS complementare per la generazione PDF.
        Non più utilizzato - il CSS è ora gestito dal template unificato.
        Mantenuto per compatibilità futura.
        """
        # CSS disabilitato - tutto gestito dal template unificato
        return None
    
    def salva_pdf_temporaneo(self, preventivo_data: PreventivoMasterModel) -> str:
        """
        Genera un PDF e lo salva in un file temporaneo
        
        Args:
            preventivo_data: Dati del preventivo
            
        Returns:
            str: Path al file temporaneo creato
        """
        pdf_content = self.genera_pdf_preventivo(preventivo_data)
        
        # Crea un file temporaneo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            return tmp_file.name
    
    def check_availability(self) -> dict:
        """
        Verifica la disponibilità del servizio PDF.
        
        Returns:
            dict: Status del servizio
        """
        return {
            "available": self.is_available,
            "weasyprint_installed": WEASYPRINT_AVAILABLE,
            "message": "✅ Export PDF disponibile" if self.is_available else 
                      "❌ Export PDF non disponibile - WeasyPrint non installato correttamente"
        } 