#!/usr/bin/env python3
"""
Script di test per verificare la funzionalità di export PDF
"""

import requests
import json
from datetime import datetime

# Dati di test per un preventivo
test_data = {
    "metadati_preventivo": {
        "id_preventivo": "00000000-0000-0000-0000-000000000001",
        "numero_preventivo": "PREV-TEST-001",
        "data_emissione": datetime.now().strftime("%Y-%m-%d"),
        "data_scadenza": "2024-12-31",
        "oggetto_preventivo": "Test Export PDF",
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
                "descrizione": "Servizio di consulenza IT",
                "quantita": 10,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 80.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0
            },
            {
                "descrizione": "Sviluppo applicazione web",
                "quantita": 5,
                "unita_misura": "giorni",
                "prezzo_unitario_netto": 500.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 10
            }
        ]
    },
    "dettagli_totali": {
        "totale_imponibile_netto": 3050.0,
        "totale_iva": 671.0,
        "totale_generale_lordo": 3721.0
    },
    "condizioni_contrattuali": {
        "testo_condizioni": "Pagamento: 30 giorni data fattura.\nValidità offerta: 30 giorni.\nConsegna: da concordare.\nI prezzi si intendono IVA esclusa."
    },
    "elementi_footer": {
        "note_finali": "Grazie per averci scelto!",
        "dati_pagamento": "Bonifico bancario - IBAN: IT00000000000000000000000",
        "validita_preventivo": "30 giorni",
        "firma_azienda": "Test Azienda S.r.l."
    }
}

def test_pdf_export():
    """Testa l'export PDF"""
    print("🧪 Test Export PDF...")
    
    try:
        # Test endpoint POST per generazione PDF
        response = requests.post(
            "http://localhost:8000/preventivo/pdf",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Salva il PDF per verifica
            with open("test_preventivo.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PDF generato con successo! Salvato come 'test_preventivo.pdf'")
            print(f"📁 Dimensione file: {len(response.content)} bytes")
        else:
            print(f"❌ Errore nella generazione PDF: {response.status_code}")
            print(f"📝 Risposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossibile connettersi al server. Assicurati che l'app sia in esecuzione su localhost:8000")
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")

def test_html_preview():
    """Testa anche la visualizzazione HTML per confronto"""
    print("\n🧪 Test Anteprima HTML...")
    
    try:
        response = requests.post(
            "http://localhost:8000/preventivo/visualizza",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            with open("test_preventivo.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML generato con successo! Salvato come 'test_preventivo.html'")
        else:
            print(f"❌ Errore nella generazione HTML: {response.status_code}")
            print(f"📝 Risposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Errore durante il test HTML: {e}")

if __name__ == "__main__":
    print("🚀 Test Servizio Export PDF")
    print("=" * 50)
    
    test_html_preview()
    test_pdf_export()
    
    print("\n✨ Test completato!")
    print("📋 Controlla i file generati: test_preventivo.html e test_preventivo.pdf") 