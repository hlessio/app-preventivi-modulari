#!/usr/bin/env python3
"""Test diretto di WeasyPrint senza server web"""

import weasyprint
from pathlib import Path

def test_weasyprint_base():
    """Test base di WeasyPrint"""
    print("🧪 Test diretto WeasyPrint...")
    
    # HTML di test semplice
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test WeasyPrint</title>
        <style>
            body {
                font-family: DejaVu Sans, Arial, sans-serif;
                margin: 2cm;
            }
            h1 {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
                padding-bottom: 10px;
            }
            .test-box {
                background-color: #f3f4f6;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>Test WeasyPrint - App Preventivi</h1>
        <div class="test-box">
            <p><strong>✅ WeasyPrint funziona correttamente!</strong></p>
            <p>Database PostgreSQL: Configurato</p>
            <p>Export PDF: Funzionante</p>
            <p>Data test: $(date)</p>
        </div>
        <p>Questo test dimostra che WeasyPrint è in grado di:</p>
        <ul>
            <li>Caricare HTML e CSS</li>
            <li>Renderizzare layout complessi</li>
            <li>Generare PDF su macOS</li>
            <li>Usare font personalizzati</li>
        </ul>
    </body>
    </html>
    """
    
    try:
        # Genera PDF dall'HTML
        pdf_content = weasyprint.HTML(string=html_content).write_pdf()
        
        # Salva il file
        output_file = Path("test_weasyprint_diretto.pdf")
        with open(output_file, "wb") as f:
            f.write(pdf_content)
        
        print(f"✅ PDF generato con successo: {output_file}")
        print(f"📄 Dimensione file: {len(pdf_content)} bytes")
        
        # Salva anche l'HTML per debug
        html_file = Path("test_weasyprint_diretto.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🔍 HTML di debug salvato: {html_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella generazione PDF: {e}")
        return False

def test_font_e_layout():
    """Test più avanzato con tabelle e layout complesso"""
    print("\n🧪 Test layout avanzato...")
    
    html_avanzato = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Layout Avanzato</title>
        <style>
            @page {
                size: A4;
                margin: 2cm 1.5cm;
            }
            body {
                font-family: DejaVu Sans, Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            .totale {
                text-align: right;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Preventivo Test</h1>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 8%">#</th>
                    <th style="width: 42%">Descrizione</th>
                    <th style="width: 8%">Qty</th>
                    <th style="width: 8%">Unità</th>
                    <th style="width: 17%">Prezzo</th>
                    <th style="width: 17%">Totale</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Sviluppo sistema preventivi modulare con integrazione PostgreSQL</td>
                    <td>40</td>
                    <td>ore</td>
                    <td>€ 50,00</td>
                    <td class="totale">€ 2.000,00</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Configurazione export PDF con WeasyPrint</td>
                    <td>8</td>
                    <td>ore</td>
                    <td>€ 50,00</td>
                    <td class="totale">€ 400,00</td>
                </tr>
            </tbody>
        </table>
        
        <div style="text-align: right; margin-top: 30px;">
            <p><strong>Subtotale: € 2.400,00</strong></p>
            <p><strong>IVA 22%: € 528,00</strong></p>
            <p style="font-size: 14px; border-top: 2px solid #333; padding-top: 10px;">
                <strong>TOTALE: € 2.928,00</strong>
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        pdf_content = weasyprint.HTML(string=html_avanzato).write_pdf()
        
        output_file = Path("test_layout_avanzato.pdf")
        with open(output_file, "wb") as f:
            f.write(pdf_content)
        
        print(f"✅ Layout avanzato generato: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Errore layout avanzato: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Test Configurazione WeasyPrint")
    print("=" * 50)
    
    # Test base
    test_base_ok = test_weasyprint_base()
    
    # Test avanzato
    test_avanzato_ok = test_font_e_layout()
    
    print("\n📊 Risultati Test:")
    print("=" * 50)
    print(f"✅ Test base: {'OK' if test_base_ok else 'ERRORE'}")
    print(f"✅ Test avanzato: {'OK' if test_avanzato_ok else 'ERRORE'}")
    
    if test_base_ok and test_avanzato_ok:
        print("\n🎉 WeasyPrint è completamente configurato e funzionante!")
        print("💡 Ora puoi utilizzare l'export PDF nell'applicazione")
    else:
        print("\n❌ Ci sono ancora problemi con la configurazione") 