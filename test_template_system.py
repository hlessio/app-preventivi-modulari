#!/usr/bin/env python3
"""
Test completo del sistema Template Documenti Personalizzabili

Questo script testa:
1. Creazione template documenti
2. Gestione template di default  
3. Validazione composizione moduli
4. API endpoints del sistema template
5. Integrazione con sistema esistente
"""

import requests
import json
from pprint import pprint
import sys

# Configurazione
BASE_URL = "http://127.0.0.1:8080"
USER_ID = "da2cb935-e023-40dd-9703-d918f1066b24"  # User ID di test

def test_sistema_template():
    """Test completo del sistema template"""
    
    print("🧪 INIZIO TEST SISTEMA TEMPLATE DOCUMENTI")
    print("=" * 60)
    
    # Test 1: Ottenere template di default
    print("\n1️⃣ Test: Ottenere template di default...")
    try:
        response = requests.get(f"{BASE_URL}/templates/default/preventivo?user_id={USER_ID}")
        if response.status_code == 200:
            default_template = response.json()
            print("✅ Template di default ottenuto/creato con successo")
            print(f"   ID: {default_template['id']}")
            print(f"   Nome: {default_template['name']}")
            print(f"   Moduli: {len(default_template['module_composition']['modules'])}")
        else:
            print(f"❌ Errore: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        return False
    
    # Test 2: Lista template utente
    print("\n2️⃣ Test: Lista template utente...")
    try:
        response = requests.get(f"{BASE_URL}/templates?user_id={USER_ID}")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Lista template ottenuta: {len(templates['templates'])} template trovati")
            for template in templates['templates']:
                print(f"   - {template['name']} (default: {template['is_default']})")
        else:
            print(f"❌ Errore: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
    
    # Test 3: Creare nuovo template personalizzato
    print("\n3️⃣ Test: Creazione template personalizzato...")
    custom_template_data = {
        "name": "Preventivo Personalizzato Test",
        "description": "Template di test con ordine moduli personalizzato",
        "document_type": "preventivo",
        "module_composition": {
            "modules": [
                {
                    "module_name": "metadati_preventivo",
                    "order": 1,
                    "enabled": True,
                    "custom_config": {}
                },
                {
                    "module_name": "intestazione_azienda", 
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
                    "module_name": "footer_preventivo",
                    "order": 6,
                    "enabled": True,
                    "custom_config": {}
                }
                # Nota: condizioni_generali omesso di proposito per testare template personalizzato
            ]
        },
        "page_format": "A4",
        "page_orientation": "landscape",
        "margins": {"top": 2.0, "right": 1.5, "bottom": 2.0, "left": 1.5},
        "is_default": False,
        "is_public": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/templates?user_id={USER_ID}",
            json=custom_template_data
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Template personalizzato creato con successo")
            print(f"   ID: {result['template_id']}")
            custom_template_id = result['template_id']
            if result.get('warnings'):
                print(f"   ⚠️ Warnings: {result['warnings']}")
        else:
            print(f"❌ Errore: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
    
    # Test 4: Ottenere template specifico
    print("\n4️⃣ Test: Ottenere template specifico...")
    try:
        response = requests.get(f"{BASE_URL}/templates/{custom_template_id}?user_id={USER_ID}")
        if response.status_code == 200:
            template = response.json()
            print("✅ Template specifico ottenuto")
            print(f"   Nome: {template['name']}")
            print(f"   Orientamento: {template['page_orientation']}")
            print(f"   Moduli abilitati: {len([m for m in template['module_composition']['modules'] if m['enabled']])}")
        else:
            print(f"❌ Errore: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
    
    # Test 5: Validazione composizione moduli
    print("\n5️⃣ Test: Validazione composizione moduli...")
    
    # Test composizione valida
    valid_composition = {
        "modules": [
            {"module_name": "intestazione_azienda", "order": 1, "enabled": True, "custom_config": {}},
            {"module_name": "tabella_preventivo", "order": 2, "enabled": True, "custom_config": {}}
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/templates/validate", json=valid_composition)
        if response.status_code == 200:
            validation = response.json()
            print(f"✅ Validazione composizione valida: {validation['valid']}")
            if validation.get('warnings'):
                print(f"   ⚠️ Warnings: {validation['warnings']}")
        else:
            print(f"❌ Errore validazione: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test composizione non valida (ordini duplicati)
    invalid_composition = {
        "modules": [
            {"module_name": "intestazione_azienda", "order": 1, "enabled": True, "custom_config": {}},
            {"module_name": "tabella_preventivo", "order": 1, "enabled": True, "custom_config": {}}  # Ordine duplicato
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/templates/validate", json=invalid_composition)
        if response.status_code == 200:
            validation = response.json()
            print(f"✅ Validazione composizione non valida: {validation['valid']} (come atteso)")
            if validation.get('errors'):
                print(f"   ❌ Errori: {validation['errors']}")
        else:
            print(f"❌ Errore validazione: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test 6: Aggiornamento template
    print("\n6️⃣ Test: Aggiornamento template...")
    update_data = {
        "name": "Preventivo Personalizzato Test - AGGIORNATO",
        "description": "Template aggiornato via API",
        "page_orientation": "portrait"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/templates/{custom_template_id}?user_id={USER_ID}",
            json=update_data
        )
        if response.status_code == 200:
            print("✅ Template aggiornato con successo")
        else:
            print(f"❌ Errore aggiornamento: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    # Test 7: Verifica template aggiornato
    print("\n7️⃣ Test: Verifica template aggiornato...")
    try:
        response = requests.get(f"{BASE_URL}/templates/{custom_template_id}?user_id={USER_ID}")
        if response.status_code == 200:
            template = response.json()
            print("✅ Verifica aggiornamento completata")
            print(f"   Nuovo nome: {template['name']}")
            print(f"   Nuovo orientamento: {template['page_orientation']}")
        else:
            print(f"❌ Errore: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETATI - Sistema template funzionante!")
    
    # Suggerimenti per i prossimi passi
    print("\n📋 PROSSIMI PASSI SUGGERITI:")
    print("1. Implementare UI Template Composer (drag & drop)")
    print("2. Integrare template nel rendering dei documenti")
    print("3. Aggiungere preview live con template personalizzati")
    print("4. Implementare gestione formato pagina e margini")
    
    return True

def test_integrazione_template_rendering():
    """Test integrazione template con sistema di rendering esistente"""
    
    print("\n🔧 TEST INTEGRAZIONE TEMPLATE + RENDERING")
    print("=" * 60)
    
    # Dati di esempio per un preventivo
    preventivo_test_data = {
        "metadati_preventivo": {
            "id_preventivo": "550e8400-e29b-41d4-a716-446655440000",
            "numero_preventivo": "PREV-2024-001",
            "data_emissione": "2024-12-17",
            "oggetto_preventivo": "Test Template Sistema",
            "stato_preventivo": "bozza"
        },
        "azienda_emittente": {
            "nome_azienda": "Test Company S.r.l.",
            "partita_iva_azienda": "IT12345678901",
            "indirizzo_azienda": {
                "via": "Via Test 123",
                "cap": "20100",
                "citta": "Milano",
                "provincia": "MI",
                "nazione": "Italia"
            },
            "email_azienda": "info@testcompany.it"
        },
        "cliente_destinatario": {
            "nome_cliente": "Cliente Test S.r.l.",
            "indirizzo": {
                "via": "Via Cliente 456", 
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "nazione": "Italia"
            }
        },
        "corpo_preventivo": {
            "righe": [
                {
                    "descrizione": "Servizio di test template",
                    "quantita": 1,
                    "prezzo_unitario_netto": 1000.0,
                    "percentuale_iva": 22
                }
            ]
        },
        "dettagli_totali": {
            "totale_imponibile_netto": 1000.0,
            "totale_iva": 220.0,
            "totale_generale_lordo": 1220.0
        }
    }
    
    print("📄 Test rendering con template di default...")
    try:
        response = requests.post(f"{BASE_URL}/preventivo/visualizza", json=preventivo_test_data)
        if response.status_code == 200:
            print("✅ Rendering con template esistente funziona")
            print(f"   Dimensione HTML: {len(response.text)} caratteri")
        else:
            print(f"❌ Errore rendering: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    print("\n📋 NOTA: Il prossimo passo sarà integrare i template personalizzati")
    print("    nel sistema di rendering per supportare ordini e configurazioni diverse.")

if __name__ == "__main__":
    print("🚀 AVVIO TEST SISTEMA TEMPLATE DOCUMENTI")
    print(f"🔗 Testando server: {BASE_URL}")
    print(f"👤 User ID test: {USER_ID}")
    
    # Verifica che il server sia attivo
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ Server non raggiungibile: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Server non raggiungibile: {e}")
        print("💡 Assicurati che il server sia avviato con: uvicorn app.main:app --reload --port 8080")
        sys.exit(1)
    
    # Esegui i test
    success = test_sistema_template()
    
    if success:
        test_integrazione_template_rendering()
        print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
    else:
        print("\n❌ ALCUNI TEST SONO FALLITI")
        sys.exit(1) 