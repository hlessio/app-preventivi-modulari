#!/usr/bin/env python3
"""
Test specifico per verificare la persistenza del template_id nei preventivi salvati.
Questo test verifica il fix per il problema dove i preventivi salvati con template personalizzati
ritornavano al template di default quando riaperti.
"""

import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000"
USER_ID = "da2cb935-e023-40dd-9703-d918f1066b24"

def create_test_template():
    """Crea un template di test personalizzato"""
    print("🔧 Creazione template di test...")
    
    template_data = {
        "name": "Template Test Persistence",
        "description": "Template per testare la persistenza del template_id",
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
                    "module_name": "tabella_preventivo",
                    "order": 3,
                    "enabled": True,
                    "custom_config": {}
                },
                {
                    "module_name": "sezione_totali",
                    "order": 4,
                    "enabled": True,
                    "custom_config": {}
                },
                # Condizioni generali DISABILITATE per test
                {
                    "module_name": "condizioni_generali",
                    "order": 5,
                    "enabled": False,
                    "custom_config": {}
                },
                {
                    "module_name": "footer_preventivo",
                    "order": 6,
                    "enabled": True,
                    "custom_config": {}
                }
            ]
        },
        "page_format": "A4",
        "page_orientation": "landscape",  # Diverso dal default per test
        "margins": {
            "top": 2.0,    # Diverso dal default per test
            "bottom": 2.0,
            "left": 1.5,
            "right": 1.5
        },
        "is_default": False,
        "is_public": False
    }
    
    response = requests.post(
        f"{BASE_URL}/templates?user_id={USER_ID}",
        headers={"Content-Type": "application/json"},
        json=template_data
    )
    
    if response.status_code == 200:
        result = response.json()
        template_id = result.get("template_id")
        print(f"✅ Template creato: {template_id}")
        return template_id
    else:
        print(f"❌ Errore creazione template: {response.status_code}")
        return None

def create_test_preventivo(template_id):
    """Crea un preventivo di test con template personalizzato"""
    print(f"💾 Creazione preventivo con template {template_id}...")
    
    preventivo_data = {
        "metadati_preventivo": {
            "id_preventivo": str(uuid4()),
            "numero_preventivo": "PERSISTENCE-TEST-001",
            "data_emissione": "2024-12-17",
            "data_scadenza": "2025-01-16",
            "oggetto_preventivo": "Test persistenza template",
            "stato_preventivo": "bozza",
            "template_id": template_id  # IMPORTANTE: includi template_id
        },
        "azienda_emittente": {
            "nome_azienda": "Test Company S.r.l.",
            "partita_iva_azienda": "IT12345678901",
            "codice_fiscale_azienda": "12345678901",
            "indirizzo_azienda": {
                "via": "Via Test 123",
                "cap": "20100",
                "citta": "Milano",
                "provincia": "MI",
                "nazione": "Italia"
            },
            "email_azienda": "test@company.it",
            "telefono_azienda": "+39 02 1234567"
        },
        "cliente_destinatario": {
            "nome_cliente": "Cliente Test Persistence",
            "partita_iva": "IT09876543210",
            "indirizzo": {
                "via": "Via Cliente 456",
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "nazione": "Italia"
            },
            "email": "cliente@test.com",
            "telefono": "+39 06 9876543",
            "referente": "Mario Rossi"
        },
        "corpo_preventivo": {
            "righe": [
                {
                    "numero_riga": 1,
                    "descrizione": "Test servizio con template personalizzato",
                    "unita_misura": "ore",
                    "quantita": 10.0,
                    "prezzo_unitario_netto": 100.0,
                    "percentuale_iva": 22.0,
                    "sconto_riga_percentuale": 0.0
                }
            ]
        },
        "condizioni_contrattuali": {
            "testo_condizioni": "Condizioni di test per template persistence"
        },
        "dettagli_totali": {
            "totale_imponibile_netto": 1000.0,
            "totale_iva": 220.0,
            "totale_generale_lordo": 1220.0
        },
        "elementi_footer": {
            "note_finali": "Preventivo test template persistence"
        },
        "user_id": USER_ID
    }
    
    response = requests.post(
        f"{BASE_URL}/preventivo/salva",
        headers={"Content-Type": "application/json"},
        json=preventivo_data
    )
    
    if response.status_code == 200:
        result = response.json()
        preventivo_id = result.get("preventivo_id")
        print(f"✅ Preventivo salvato: {preventivo_id}")
        return preventivo_id
    else:
        print(f"❌ Errore salvataggio preventivo: {response.status_code} - {response.text}")
        return None

def test_preventivo_template_persistence(preventivo_id, template_id):
    """Test che il template_id sia persistente nel preventivo"""
    print(f"🔍 Test persistenza template per preventivo {preventivo_id}...")
    
    # 1. Carica il preventivo dal database
    response = requests.get(f"{BASE_URL}/preventivo/{preventivo_id}?user_id={USER_ID}")
    
    if response.status_code != 200:
        print(f"❌ Errore caricamento preventivo: {response.status_code}")
        return False
    
    preventivo_data = response.json()
    
    # 2. Verifica che il template_id sia presente nei metadati
    saved_template_id = preventivo_data.get("metadati_preventivo", {}).get("template_id")
    
    if saved_template_id == template_id:
        print(f"✅ Template ID correttamente salvato: {saved_template_id}")
    else:
        print(f"❌ Template ID non salvato correttamente. Atteso: {template_id}, Trovato: {saved_template_id}")
        return False
    
    # 3. Test visualizzazione con template salvato
    response = requests.get(f"{BASE_URL}/preventivo/{preventivo_id}/visualizza?user_id={USER_ID}")
    
    if response.status_code != 200:
        print(f"❌ Errore visualizzazione preventivo: {response.status_code}")
        return False
    
    html_content = response.text
    
    # 4. Verifica che il modulo disabilitato non sia presente
    if "Condizioni Generali" not in html_content:
        print("✅ Template personalizzato applicato: modulo disabilitato non presente")
    else:
        print("❌ Template di default utilizzato: modulo disabilitato presente")
        return False
    
    # 5. Verifica orientamento landscape nel template
    if "landscape" in html_content.lower() or "21cm" in html_content:  # Orientamento landscape
        print("✅ Configurazione template personalizzato applicata (landscape)")
    else:
        print("⚠️  Non è possibile verificare l'orientamento dall'HTML")
    
    return True

def cleanup_test_data(template_id, preventivo_id):
    """Pulizia dati di test"""
    print("🧹 Pulizia dati di test...")
    
    # Non eliminiamo il preventivo per ora (non c'è endpoint delete)
    # Elimina solo il template
    if template_id:
        response = requests.delete(f"{BASE_URL}/templates/{template_id}?user_id={USER_ID}")
        if response.status_code == 200:
            print("✅ Template di test eliminato")
        else:
            print(f"⚠️  Errore eliminazione template: {response.status_code}")

def main():
    """Test principale"""
    print("🚀 Test Persistenza Template ID nei Preventivi\n")
    
    template_id = None
    preventivo_id = None
    
    try:
        # 1. Crea template di test
        template_id = create_test_template()
        if not template_id:
            print("❌ Impossibile procedere senza template")
            return
        
        # 2. Crea preventivo con template personalizzato
        preventivo_id = create_test_preventivo(template_id)
        if not preventivo_id:
            print("❌ Impossibile procedere senza preventivo")
            return
        
        # 3. Test persistenza template
        success = test_preventivo_template_persistence(preventivo_id, template_id)
        
        if success:
            print("\n🎉 TEST SUPERATO! Template ID persistente correttamente")
            print("📋 Riepilogo:")
            print(f"   ✅ Template creato: {template_id}")
            print(f"   ✅ Preventivo salvato: {preventivo_id}")
            print(f"   ✅ Template ID salvato nei metadati")
            print(f"   ✅ Template personalizzato applicato alla visualizzazione")
            print(f"   ✅ Moduli disabilitati esclusi dal rendering")
        else:
            print("\n❌ TEST FALLITO! Template ID non persistente")
            
    except Exception as e:
        print(f"\n💥 Errore durante il test: {e}")
    finally:
        # Pulizia
        cleanup_test_data(template_id, preventivo_id)

if __name__ == "__main__":
    main() 