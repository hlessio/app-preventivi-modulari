#!/usr/bin/env python3
"""
Test completo di integrazione per il sistema Template Documents
Verifica Dashboard -> Template Composer -> Form Preventivo -> Template personalizzati
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
USER_ID = "da2cb935-e023-40dd-9703-d918f1066b24"

def test_dashboard_links():
    """
    Verifica che la dashboard carichi correttamente e abbia i link al Template Composer
    """
    print("🧪 Test: Dashboard con link Template Composer...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            content = response.text
            if "Template Composer" in content:
                print("✅ Link Template Composer presente nella dashboard")
                if "/templates/composer" in content:
                    print("✅ URL Template Composer corretto")
                    return True
                else:
                    print("❌ URL Template Composer non trovato")
                    return False
            else:
                print("❌ Link Template Composer non trovato nella dashboard")
                return False
        else:
            print(f"❌ Errore caricamento dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore connessione dashboard: {e}")
        return False

def test_template_composer_complete():
    """
    Test completo del Template Composer
    """
    print("\n🧪 Test: Template Composer completo...")
    
    try:
        # 1. Verifica caricamento pagina
        response = requests.get(f"{BASE_URL}/templates/composer")
        if response.status_code != 200:
            print(f"❌ Errore caricamento Template Composer: {response.status_code}")
            return False
        
        print("✅ Template Composer caricato")
        
        # 2. Crea un template di test
        template_data = {
            "name": "Test Integration Template",
            "description": "Template creato durante test di integrazione",
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
                        "module_name": "intestazione_cliente",
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
                        "module_name": "condizioni_generali",
                        "order": 4,
                        "enabled": False,  # Disabilitato per test
                        "custom_config": {}
                    },
                    {
                        "module_name": "footer_preventivo",
                        "order": 5,
                        "enabled": True,
                        "custom_config": {}
                    }
                ]
            },
            "page_format": "A4",
            "page_orientation": "portrait",
            "margins": {
                "top": 1.5,
                "bottom": 1.5,
                "left": 1.0,
                "right": 1.0
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
            print(f"✅ Template creato con ID: {template_id}")
            return template_id
        else:
            print(f"❌ Errore creazione template: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Errore test Template Composer: {e}")
        return False

def test_templates_list():
    """
    Test lista template per form preventivo
    """
    print("\n🧪 Test: Lista template per form preventivo...")
    
    try:
        response = requests.get(f"{BASE_URL}/templates?user_id={USER_ID}&document_type=preventivo")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get("templates", [])
            print(f"✅ Trovati {len(templates)} template disponibili")
            
            for template in templates[:3]:  # Mostra solo i primi 3
                print(f"   - {template['name']} (ID: {template['id']})")
            
            return templates
        else:
            print(f"❌ Errore recupero lista template: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Errore test lista template: {e}")
        return []

def test_preventivo_form_with_template(template_id=None):
    """
    Test form preventivo con template personalizzato
    """
    print("\n🧪 Test: Form preventivo con template personalizzato...")
    
    try:
        # 1. Verifica caricamento form
        response = requests.get(f"{BASE_URL}/preventivo/nuovo")
        if response.status_code != 200:
            print(f"❌ Errore caricamento form preventivo: {response.status_code}")
            return False
        
        print("✅ Form preventivo caricato")
        
        # 2. Test anteprima con template personalizzato
        if template_id:
            sample_data = create_sample_preventivo_data()
            
            response = requests.post(
                f"{BASE_URL}/preventivo/visualizza?template_id={template_id}",
                headers={"Content-Type": "application/json"},
                json=sample_data
            )
            
            if response.status_code == 200:
                print(f"✅ Anteprima con template {template_id} funziona")
                
                # Verifica che il modulo disabilitato non sia presente
                content = response.text
                if "Condizioni Generali" not in content:
                    print("✅ Modulo disabilitato correttamente escluso dall'anteprima")
                else:
                    print("⚠️  Modulo disabilitato presente nell'anteprima")
                
                return True
            else:
                print(f"❌ Errore anteprima con template: {response.status_code}")
                return False
        else:
            print("⚠️  Nessun template fornito per test")
            return False
            
    except Exception as e:
        print(f"❌ Errore test form preventivo: {e}")
        return False

def test_template_management_operations(template_id):
    """
    Test operazioni di gestione template (load, update, delete)
    """
    print("\n🧪 Test: Operazioni gestione template...")
    
    try:
        # 1. Carica template specifico
        response = requests.get(f"{BASE_URL}/templates/{template_id}?user_id={USER_ID}")
        if response.status_code == 200:
            template_data = response.json()
            print(f"✅ Template caricato: {template_data['name']}")
        else:
            print(f"❌ Errore caricamento template: {response.status_code}")
            return False
        
        # 2. Aggiorna template
        update_data = {
            "name": "Test Integration Template - UPDATED",
            "description": "Template aggiornato durante test"
        }
        
        response = requests.put(
            f"{BASE_URL}/templates/{template_id}?user_id={USER_ID}",
            headers={"Content-Type": "application/json"},
            json=update_data
        )
        
        if response.status_code == 200:
            print("✅ Template aggiornato con successo")
        else:
            print(f"❌ Errore aggiornamento template: {response.status_code}")
            return False
        
        # 3. Elimina template
        response = requests.delete(f"{BASE_URL}/templates/{template_id}?user_id={USER_ID}")
        if response.status_code == 200:
            print("✅ Template eliminato con successo")
            return True
        else:
            print(f"❌ Errore eliminazione template: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore test gestione template: {e}")
        return False

def create_sample_preventivo_data():
    """
    Crea dati di esempio per preventivo
    """
    from uuid import uuid4
    
    return {
        "metadati_preventivo": {
            "id_preventivo": str(uuid4()),
            "numero_preventivo": "TEST-INT-001",
            "data_emissione": "2024-12-17",
            "data_scadenza": "2025-01-16",
            "oggetto_preventivo": "Test Integrazione Template System",
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
            "nome_cliente": "Cliente Test Integrazione",
            "partita_iva": "IT09876543210",
            "codice_fiscale": "RSSMRA80A01H501Z",
            "indirizzo": {
                "via": "Via Milano 456",
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "nazione": "Italia"
            },
            "email": "test@integrazione.com",
            "telefono": "+39 06 9876543",
            "referente": "Mario Rossi"
        },
        "corpo_preventivo": {
            "righe": [
                {
                    "numero_riga": 1,
                    "descrizione": "Test integrazione sistema template",
                    "unita_misura": "ore",
                    "quantita": 10.0,
                    "prezzo_unitario_netto": 100.0,
                    "percentuale_iva": 22.0,
                    "sconto_riga_percentuale": 0.0,
                    "note_riga": "Test personalizzazione template"
                }
            ],
            "note_tabella": "Preventivo di test per sistema template"
        },
        "condizioni_contrattuali": {
            "testo_condizioni": "Condizioni di test per integrazione template system"
        },
        "dettagli_totali": {
            "totale_imponibile_netto": 1000.0,
            "totale_iva": 220.0,
            "totale_generale_lordo": 1220.0
        },
        "elementi_footer": {
            "dati_pagamento": "Test payment",
            "validita_preventivo": "30 giorni",
            "note_finali": "Test integrazione completata",
            "firma_azienda": "TechSolutions Test"
        }
    }

def main():
    """
    Esegue tutti i test di integrazione
    """
    print("🚀 Avvio test integrazione completa Template System\n")
    
    # Test 1: Dashboard
    test1 = test_dashboard_links()
    
    # Test 2: Template Composer
    template_id = test_template_composer_complete()
    test2 = bool(template_id)
    
    # Test 3: Lista template
    templates = test_templates_list()
    test3 = len(templates) > 0
    
    # Test 4: Form preventivo con template
    test4 = test_preventivo_form_with_template(template_id) if template_id else False
    
    # Test 5: Gestione template
    test5 = test_template_management_operations(template_id) if template_id else False
    
    print(f"\n📊 Risultati test integrazione:")
    print(f"   Dashboard link: {'✅' if test1 else '❌'}")
    print(f"   Template Composer: {'✅' if test2 else '❌'}")
    print(f"   Lista template: {'✅' if test3 else '❌'}")
    print(f"   Form con template: {'✅' if test4 else '❌'}")
    print(f"   Gestione template: {'✅' if test5 else '❌'}")
    
    success_count = sum([test1, test2, test3, test4, test5])
    total_tests = 5
    
    if success_count == total_tests:
        print(f"\n🎉 Tutti i test superati! Sistema Template completamente integrato.")
        print(f"📈 Funzionalità operative:")
        print(f"   ✅ Dashboard con accesso Template Composer")
        print(f"   ✅ Template Composer per creare/modificare template")
        print(f"   ✅ Selezione template nel form preventivo")
        print(f"   ✅ Anteprima con template personalizzati")
        print(f"   ✅ Gestione completa template (CRUD)")
    else:
        print(f"\n⚠️  {success_count}/{total_tests} test superati. Verificare i log per dettagli.")

if __name__ == "__main__":
    main() 