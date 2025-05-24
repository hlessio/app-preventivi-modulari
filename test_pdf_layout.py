#!/usr/bin/env python3
"""
Test specifico per l'impaginazione PDF con dati complessi
"""

import requests
import json
from datetime import datetime

# Dati di test con più voci per testare l'impaginazione
test_data_complesso = {
    "metadati_preventivo": {
        "id_preventivo": "12345678-1234-1234-1234-123456789abc",
        "numero_preventivo": "PREV-LAYOUT-001",
        "data_emissione": datetime.now().strftime("%Y-%m-%d"),
        "data_scadenza": "2024-12-31",
        "oggetto_preventivo": "Test Impaginazione PDF - Sistema preventivi modulare con tabelle estese",
        "stato_preventivo": "bozza"
    },
    "azienda_emittente": {
        "nome_azienda": "Test Azienda S.r.l.",
        "partita_iva_azienda": "12345678901",
        "indirizzo_azienda": {
            "via": "Via Test 123",
            "cap": "00100",
            "citta": "Roma",
            "provincia": "RM",
            "nazione": "Italia"
        },
        "email_azienda": "info@testazienda.it",
        "telefono_azienda": "+39 06 1234567"
    },
    "cliente_destinatario": {
        "nome_cliente": "Cliente Test S.r.l.",
        "indirizzo": {
            "via": "Via Cliente 456",
            "cap": "20100",
            "citta": "Milano",
            "provincia": "MI",
            "nazione": "Italia"
        },
        "email": "test@cliente.it",
        "telefono": "+39 02 7654321",
        "partita_iva": "98765432109"
    },
    "corpo_preventivo": {
        "righe": [
            {
                "descrizione": "Analisi preliminare e studio di fattibilità del progetto web",
                "quantita": 8,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 85.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0,
                "note_riga": "Include analisi requisiti, studio UX/UI e definizione architettura"
            },
            {
                "descrizione": "Sviluppo backend con Python/FastAPI e database PostgreSQL",
                "quantita": 20,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 75.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 5,
                "note_riga": "API REST, modelli dati, servizi business logic"
            },
            {
                "descrizione": "Frontend responsive con HTML5, CSS3, JavaScript e HTMX",
                "quantita": 15,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 70.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0,
                "note_riga": "Interfaccia utente moderna, mobile-first design"
            },
            {
                "descrizione": "Sistema di export PDF con WeasyPrint e template ottimizzati",
                "quantita": 6,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 80.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0,
                "note_riga": "Template A4, CSS print-ready, numerazione pagine"
            },
            {
                "descrizione": "Testing, debugging e ottimizzazione performance",
                "quantita": 4,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 65.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 10,
                "note_riga": "Test funzionali, fix bug, ottimizzazione query DB"
            },
            {
                "descrizione": "Documentazione tecnica e manuale utente",
                "quantita": 3,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 60.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0,
                "note_riga": "README, API docs, guida installazione"
            },
            {
                "descrizione": "Deploy e configurazione ambiente di produzione",
                "quantita": 4,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 90.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0,
                "note_riga": "Setup cloud, CI/CD, monitoraggio"
            }
        ]
    },
    "dettagli_totali": {
        "totale_imponibile_netto": 4200.0,
        "totale_iva": 924.0,
        "totale_generale_lordo": 5124.0
    },
    "condizioni_contrattuali": {
        "testo_condizioni": """CONDIZIONI GENERALI DI CONTRATTO

1. PAGAMENTO: Il pagamento dovrà essere effettuato entro 30 giorni dalla data di emissione della fattura.

2. VALIDITÀ OFFERTA: La presente offerta è valida per 30 giorni dalla data di emissione.

3. CONSEGNA: I tempi di consegna indicati sono puramente indicativi e non costituiscono termine essenziale.

4. GARANZIA: Il lavoro svolto è garantito per 12 mesi dalla data di consegna.

5. PROPRIETÀ INTELLETTUALE: Il codice sviluppato rimane di proprietà del cliente al completamento del pagamento.

6. MODIFICHE: Eventuali modifiche ai requisiti saranno fatturate separatamente."""
    },
    "elementi_footer": {
        "note_finali": "Grazie per averci scelto come partner tecnologico per il vostro progetto!",
        "dati_pagamento": "Bonifico bancario - IBAN: IT60 X054 2811 1010 0000 0123 456",
        "validita_preventivo": "30 giorni",
        "firma_azienda": "Test Azienda S.r.l. - Ing. Mario Rossi"
    }
}

def test_pdf_layout_complesso():
    """Testa l'export PDF con layout complesso"""
    print("🧪 Test Layout PDF Complesso...")
    
    try:
        # Test endpoint POST per generazione PDF
        response = requests.post(
            "http://localhost:8000/preventivo/pdf",
            json=test_data_complesso,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Salva il PDF per verifica
            with open("test_layout_complesso.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PDF layout complesso generato! Salvato come 'test_layout_complesso.pdf'")
            print(f"📁 Dimensione file: {len(response.content)} bytes")
        else:
            print(f"❌ Errore nella generazione PDF: {response.status_code}")
            print(f"📝 Risposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server non raggiungibile. Assicurati che sia in esecuzione su localhost:8000")
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")

def test_html_preview_complesso():
    """Testa anche la visualizzazione HTML per confronto"""
    print("\n🧪 Test Anteprima HTML Complessa...")
    
    try:
        response = requests.post(
            "http://localhost:8000/preventivo/visualizza",
            json=test_data_complesso,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            with open("test_layout_complesso.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML layout complesso generato! Salvato come 'test_layout_complesso.html'")
        else:
            print(f"❌ Errore nella generazione HTML: {response.status_code}")
            print(f"📝 Risposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Errore durante il test HTML: {e}")

if __name__ == "__main__":
    print("🚀 Test Layout PDF Complesso")
    print("=" * 50)
    
    test_html_preview_complesso()
    test_pdf_layout_complesso()
    
    print("\n✨ Test completato!")
    print("📋 Controlla i file generati:")
    print("   - test_layout_complesso.html")
    print("   - test_layout_complesso.pdf")
    print("\n💡 Verifica che:")
    print("   - La tabella non sia tagliata lateralmente")
    print("   - I testi lunghi vadano a capo correttamente")
    print("   - I margini siano corretti")
    print("   - Le condizioni generali siano leggibili") 