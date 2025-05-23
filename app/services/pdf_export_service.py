from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Optional
import tempfile
import os

from ..models import PreventivoMasterModel
from ..services.preventivo_calculator import calcola_totali_preventivo


class PDFExportService:
    """
    Servizio per l'export di preventivi in formato PDF usando WeasyPrint
    """
    
    def __init__(self, templates_dir: Path):
        """
        Inizializza il servizio con la directory dei template
        
        Args:
            templates_dir: Path alla directory contenente i template Jinja2
        """
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))
        
    def genera_pdf_preventivo(self, preventivo_data: PreventivoMasterModel) -> bytes:
        """
        Genera un PDF del preventivo a partire dai dati forniti
        
        Args:
            preventivo_data: Dati del preventivo da convertire in PDF
            
        Returns:
            bytes: Il contenuto del PDF generato
            
        Raises:
            Exception: Se c'è un errore nella generazione del PDF
        """
        try:
            # Assicuriamoci che i totali siano calcolati
            calcola_totali_preventivo(preventivo_data)
            
            # Renderizza l'HTML usando il template PDF
            html_content = self._renderizza_html_pdf(preventivo_data)
            
            # Genera e restituisce il PDF
            return self._genera_pdf_da_html(html_content)
            
        except Exception as e:
            raise Exception(f"Errore nella generazione del PDF: {str(e)}")
    
    def _renderizza_html_pdf(self, preventivo_data: PreventivoMasterModel) -> str:
        """
        Renderizza l'HTML del preventivo usando il template specifico per PDF
        
        Args:
            preventivo_data: Dati del preventivo
            
        Returns:
            str: HTML renderizzato
        """
        # Usa il template specifico per PDF o fallback al template normale
        template_name = "preventivo/preventivo_pdf.html"
        
        try:
            template = self.env.get_template(template_name)
        except:
            # Fallback al template normale se quello PDF non esiste
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
        # CSS specifico per la stampa PDF
        pdf_css = CSS(string="""
            @page {
                size: A4;
                margin: 2cm 1.5cm;
                @bottom-center {
                    content: "Pagina " counter(page) " di " counter(pages);
                    font-size: 9px;
                    color: #666;
                }
            }
            
            body {
                font-family: 'DejaVu Sans', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.3;
                color: #333;
            }
            
            .container {
                width: 100%;
                margin: 0;
                padding: 0;
                border: none;
                box-shadow: none;
                max-width: 100%;
                box-sizing: border-box;
            }
            
            header, footer, section {
                margin-bottom: 12px;
                padding: 8px 0;
                border: none;
                page-break-inside: avoid;
            }
            
            header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                border-bottom: 2px solid #2c3e50;
                margin-bottom: 20px;
            }
            
            .company-logo {
                max-width: 100px;
                max-height: 50px;
            }
            
            h1, h2, h3 {
                color: #2c3e50;
                margin-top: 0;
                margin-bottom: 8px;
            }
            
            h1 { font-size: 20px; }
            h2 { font-size: 16px; margin-bottom: 8px; }
            h3 { font-size: 13px; }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
                page-break-inside: avoid;
                table-layout: fixed;
            }
            
            th, td {
                border: 1px solid #ddd;
                padding: 6px;
                text-align: left;
                font-size: 10px;
                vertical-align: top;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            
            th {
                background-color: #f8f9fa;
                font-weight: bold;
                font-size: 9px;
            }
            
            /* Larghezze specifiche per tabella prodotti */
            .tabella-prodotti th:nth-child(1),
            .tabella-prodotti td:nth-child(1) { width: 8%; }
            .tabella-prodotti th:nth-child(2),
            .tabella-prodotti td:nth-child(2) { width: 42%; }
            .tabella-prodotti th:nth-child(3),
            .tabella-prodotti td:nth-child(3) { width: 8%; }
            .tabella-prodotti th:nth-child(4),
            .tabella-prodotti td:nth-child(4) { width: 8%; }
            .tabella-prodotti th:nth-child(5),
            .tabella-prodotti td:nth-child(5) { width: 17%; }
            .tabella-prodotti th:nth-child(6),
            .tabella-prodotti td:nth-child(6) { width: 17%; }
            
            .totals {
                float: right;
                width: 250px;
                clear: both;
                margin-top: 15px;
            }
            
            .totals td {
                text-align: right;
                font-weight: bold;
                font-size: 10px;
                padding: 4px;
            }
            
            .text-right {
                text-align: right;
            }
            
            .text-center {
                text-align: center;
            }
            
            .notes {
                white-space: pre-wrap;
                font-size: 9px;
                background-color: #f8f9fa;
                padding: 8px;
                border-left: 3px solid #2c3e50;
                word-wrap: break-word;
            }
            
            .numero-riga {
                text-align: center;
                background-color: #f8f9fa;
                font-size: 9px;
            }
            
            .descrizione-compatta {
                line-height: 1.2;
                font-size: 9px;
            }
            
            .prezzo {
                font-size: 9px;
                white-space: nowrap;
            }
            
            /* Evita interruzioni di pagina indesiderate */
            .totals, .condizioni {
                page-break-inside: avoid;
            }
            
            /* Stili per nascondere elementi non necessari in PDF */
            .no-print {
                display: none !important;
            }
        """)
        
        # Crea il documento HTML
        html_doc = HTML(string=html_content)
        
        # Genera il PDF
        return html_doc.write_pdf(stylesheets=[pdf_css])

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