#!/usr/bin/env python3
"""
Script di test veloce per verificare l'export PDF ottimizzato
"""

import requests
from datetime import datetime

# Dati di test compatti
test_data = {
    "metadati_preventivo": {
        "id_preventivo": "00000000-0000-0000-0000-000000000001",
        "numero_preventivo": "PREV-LAYOUT-TEST",
        "data_emissione": datetime.now().strftime("%Y-%m-%d"),
        "oggetto_preventivo": "Test Layout Ottimizzato",
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
        "nome_cliente": "Cliente con Nome Molto Lungo per Testare Word Wrapping S.r.l.",
        "indirizzo": {
            "via": "Via del Cliente con Indirizzo Molto Lungo per Testare il Layout 456",
            "cap": "20100",
            "citta": "Milano",
            "provincia": "MI",
            "nazione": "Italia"
        },
        "email": "test@clienteconemailtroppolungadagestionare.it",
        "telefono": "+39 02 7654321",
        "partita_iva": "98765432109"
    },
    "corpo_preventivo": {
        "righe": [
            {
                "descrizione": "Servizio di consulenza IT con descrizione molto lunga per testare il word wrapping nelle celle della tabella",
                "quantita": 10,
                "unita_misura": "ore",
                "prezzo_unitario_netto": 80.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 0
            },
            {
                "descrizione": "Sviluppo applicazione web complessa",
                "quantita": 5,
                "unita_misura": "giorni",
                "prezzo_unitario_netto": 500.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 10
            },
            {
                "descrizione": "Servizio di manutenzione",
                "quantita": 12,
                "unita_misura": "mesi",
                "prezzo_unitario_netto": 150.0,
                "percentuale_iva": 22,
                "sconto_riga_percentuale": 5
            }
        ]
    },
    "dettagli_totali": {
        "totale_imponibile_netto": 4960.0,
        "totale_iva": 1091.2,
        "totale_generale_lordo": 6051.2
    },
    "condizioni_contrattuali": {
        "testo_condizioni": "Pagamento: 30 giorni data fattura.\nValidità offerta: 30 giorni.\nConsegna: da concordare.\nI prezzi si intendono IVA esclusa.\nCondizione aggiuntiva molto lunga per testare il word wrapping nel footer del documento."
    },
    "elementi_footer": {
        "note_finali": "Grazie per averci scelto! Nota molto lunga per testare il layout del footer.",
        "dati_pagamento": "Bonifico bancario - IBAN: IT00000000000000000000000",
        "validita_preventivo": "30 giorni",
        "firma_azienda": "Test Azienda S.r.l."
    }
}

def quick_test():
    print("🧪 Test Rapido Layout PDF Ottimizzato")
    print("=" * 45)
    
    try:
        response = requests.post(
            "http://localhost:8000/preventivo/pdf",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ PDF generato correttamente!")
            print(f"📁 Dimensione: {len(response.content)} bytes")
            print("🎯 Layout ottimizzato applicato con successo")
            
            # Salva temporaneamente per verifica manuale
            with open("temp_test.pdf", "wb") as f:
                f.write(response.content)
            print("💾 File temporaneo salvato come 'temp_test.pdf'")
            print("🗑️  Ricorda di eliminarlo dopo la verifica: rm temp_test.pdf")
            
        else:
            print(f"❌ Errore HTTP {response.status_code}")
            print(f"📝 Dettagli: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server non raggiungibile su localhost:8000")
        print("💡 Avvia il server con: ./setup_weasyprint.sh && python -m uvicorn app.main:app --reload --port 8000")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    quick_test() 