#!/usr/bin/env python3
"""
Test per verificare il funzionamento del Template Composer e della funzionalità di anteprima
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_template_composer_page():
    """
    Testa che la pagina del Template Composer si carichi correttamente
    """
    print("🧪 Test: Caricamento pagina Template Composer...")
    
    try:
        response = requests.get(f"{BASE_URL}/templates/composer")
        
        if response.status_code == 200:
            print("✅ Pagina Template Composer caricata con successo")
            
            # Verifica che contenga gli elementi chiave
            content = response.text
            if "Template Document Composer" in content:
                print("✅ Titolo pagina presente")
            if "Moduli Disponibili" in content:
                print("✅ Sezione moduli disponibili presente")
            if "Configurazione Template" in content:
                print("✅ Sezione configurazione presente")
            if "Anteprima" in content:
                print("✅ Sezione anteprima presente")
            
            return True
        else:
            print(f"❌ Errore caricamento pagina: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False

def create_sample_preventivo_data() -> Dict[str, Any]:
    """
    Crea dati di esempio per un preventivo usando la struttura corretta di PreventivoMasterModel
    """
    from uuid import uuid4
    from datetime import date
    
    return {
        "metadati_preventivo": {
            "id_preventivo": str(uuid4()),
            "numero_preventivo": "PREV-2024-001",
            "data_emissione": "2024-12-17",
            "data_scadenza": "2025-01-16",
            "oggetto_preventivo": "Test Template Composer",
            "stato_preventivo": "bozza"
        },
        "azienda_emittente": {
            "nome_azienda": "TechSolutions S.r.l.",
            "partita_iva_azienda": "IT12345678901",
            "codice_fiscale_azienda": "12345678901",
            "indirizzo_azienda": {
                "via": "Via Roma 123",
                "cap": "20100",
                "citta": "Milano",
                "provincia": "MI",
                "nazione": "Italia"
            },
            "email_azienda": "info@techsolutions.it",
            "telefono_azienda": "+39 02 1234567",
            "sito_web_azienda": "https://www.techsolutions.it"
        },
        "cliente_destinatario": {
            "nome_cliente": "Cliente Test S.r.l.",
            "partita_iva": "IT09876543210",
            "codice_fiscale": "RSSMRA80A01H501Z",
            "indirizzo": {
                "via": "Via Milano 456",
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "nazione": "Italia"
            },
            "email": "mario.rossi@test.com",
            "telefono": "+39 06 9876543",
            "referente": "Mario Rossi"
        },
        "corpo_preventivo": {
            "righe": [
                {
                    "numero_riga": 1,
                    "descrizione": "Consulenza iniziale",
                    "unita_misura": "ore",
                    "quantita": 10.0,
                    "prezzo_unitario_netto": 85.0,
                    "percentuale_iva": 22.0,
                    "sconto_riga_percentuale": 0.0,
                    "note_riga": "Analisi requisiti"
                },
                {
                    "numero_riga": 2,
                    "descrizione": "Sviluppo software",
                    "unita_misura": "ore",
                    "quantita": 20.0,
                    "prezzo_unitario_netto": 75.0,
                    "percentuale_iva": 22.0,
                    "sconto_riga_percentuale": 5.0,
                    "note_riga": "Codifica e testing"
                }
            ],
            "note_tabella": "Note generali del preventivo"
        },
        "condizioni_contrattuali": {
            "testo_condizioni": "Condizioni di pagamento: 30% all'ordine, 70% alla consegna. Modalità: Bonifico bancario. Tempi di consegna: 4 settimane. Garanzia: 12 mesi. Validità offerta: 30 giorni."
        },
        "dettagli_totali": {
            "totale_imponibile_netto": 1275.0,  # Verrà ricalcolato
            "totale_iva": 280.5,  # Verrà ricalcolato
            "totale_generale_lordo": 1555.5  # Verrà ricalcolato
        },
        "elementi_footer": {
            "dati_pagamento": "Bonifico bancario",
            "validita_preventivo": "30 giorni",
            "note_finali": "Grazie per la fiducia",
            "firma_azienda": "TechSolutions S.r.l."
        }
    }

def create_sample_template_config() -> Dict[str, Any]:
    """
    Crea configurazione template di esempio
    """
    return {
        "name": "Template Test",
        "description": "Configurazione di test per l'anteprima",
        "document_type": "preventivo",
        "module_composition": {
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
        },
        "page_format": "A4",
        "page_orientation": "portrait",
        "margins": {
            "top": 1.2,
            "bottom": 1.2,
            "left": 0.8,
            "right": 0.8
        },
        "custom_styles": ""
    }

def test_preview_endpoint():
    """
    Testa l'endpoint di anteprima
    """
    print("\n🧪 Test: Endpoint anteprima preventivo...")
    
    try:
        # Prepara i dati
        preventivo_data = create_sample_preventivo_data()
        template_config = create_sample_template_config()
        
        payload = {
            "preventivo_data": preventivo_data,
            "template_config": template_config
        }
        
        # Invia richiesta
        response = requests.post(
            f"{BASE_URL}/preventivo/preview",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Endpoint anteprima funziona correttamente")
            
            # Verifica che sia HTML
            content = response.text
            if "<html" in content.lower() and "</html>" in content.lower():
                print("✅ Risposta contiene HTML valido")
            
            # Verifica presenza dati di esempio
            if "TechSolutions S.r.l." in content:
                print("✅ Dati azienda presenti nell'anteprima")
            if "Cliente Test" in content:
                print("✅ Dati cliente presenti nell'anteprima")
            if "PREV-2024-001" in content:
                print("✅ Numero preventivo presente nell'anteprima")
            
            # Salva l'anteprima per ispezione visuale
            with open("test_preview_output.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ Anteprima salvata in test_preview_output.html")
            
            return True
        else:
            print(f"❌ Errore endpoint anteprima: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Errore test anteprima: {e}")
        return False

def test_template_config_only():
    """
    Testa anteprima con solo alcuni moduli abilitati
    """
    print("\n🧪 Test: Anteprima con configurazione parziale...")
    
    try:
        preventivo_data = create_sample_preventivo_data()
        template_config = create_sample_template_config()
        
        # Abilita solo alcuni moduli per test
        template_config["module_composition"]["modules"] = [
            {
                "module_name": "intestazione_azienda",
                "order": 1,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "intestazione_cliente", 
                "order": 2,
                "enabled": True,
                "custom_config": {}
            },
            {
                "module_name": "tabella_preventivo",
                "order": 3,
                "enabled": False,  # Disabilitato
                "custom_config": {}
            },
            {
                "module_name": "footer_preventivo",
                "order": 4,
                "enabled": True,
                "custom_config": {}
            }
        ]
        
        payload = {
            "preventivo_data": preventivo_data,
            "template_config": template_config
        }
        
        response = requests.post(
            f"{BASE_URL}/preventivo/preview",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Anteprima con configurazione parziale funziona")
            
            content = response.text
            # La tabella non dovrebbe essere presente (modulo disabilitato)
            if "Consulenza iniziale" not in content:
                print("✅ Modulo disabilitato correttamente escluso")
            else:
                print("⚠️  Modulo disabilitato presente nell'anteprima")
            
            return True
        else:
            print(f"❌ Errore anteprima parziale: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore test configurazione parziale: {e}")
        return False

def main():
    """
    Esegue tutti i test
    """
    print("🚀 Avvio test Template Composer\n")
    
    # Test caricamento pagina
    test1 = test_template_composer_page()
    
    # Test endpoint anteprima
    test2 = test_preview_endpoint()
    
    # Test configurazione parziale
    test3 = test_template_config_only()
    
    print(f"\n📊 Risultati test:")
    print(f"   Caricamento pagina: {'✅' if test1 else '❌'}")
    print(f"   Endpoint anteprima: {'✅' if test2 else '❌'}")  
    print(f"   Configurazione parziale: {'✅' if test3 else '❌'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 Tutti i test superati! Template Composer pronto per l'uso.")
    else:
        print("\n⚠️  Alcuni test falliti. Verificare i log per dettagli.")

if __name__ == "__main__":
    main() 