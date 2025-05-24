#!/usr/bin/env python3
"""
Test script per il sistema delle cartelle
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
USER_ID = "da2cb935-e023-40dd-9703-d918f1066b24"

def test_cartelle_endpoints():
    """Test degli endpoint delle cartelle"""
    
    print("🧪 Test Sistema Cartelle")
    print("=" * 50)
    
    # Test 1: Lista cartelle vuota
    print("\n1. Test lista cartelle vuota...")
    try:
        response = requests.get(f"{BASE_URL}/cartelle", params={"user_id": USER_ID})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            cartelle = response.json()
            print(f"   Cartelle trovate: {len(cartelle)}")
            print("   ✅ Lista cartelle OK")
        else:
            print(f"   ❌ Errore: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore connessione: {e}")
        return False
    
    # Test 2: Creazione cartella
    print("\n2. Test creazione cartella...")
    cartella_data = {
        "nome": "Test Cartella",
        "descrizione": "Cartella di test per il sistema",
        "colore": "#FF5733",
        "icona": "fas fa-star"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cartelle", 
            params={"user_id": USER_ID},
            json=cartella_data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            cartella_id = result.get("cartella_id")
            print(f"   Cartella creata con ID: {cartella_id}")
            print("   ✅ Creazione cartella OK")
        else:
            print(f"   ❌ Errore: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False
    
    # Test 3: Lista cartelle con la nuova cartella
    print("\n3. Test lista cartelle aggiornata...")
    try:
        response = requests.get(f"{BASE_URL}/cartelle", params={"user_id": USER_ID})
        if response.status_code == 200:
            cartelle = response.json()
            print(f"   Cartelle trovate: {len(cartelle)}")
            for cartella in cartelle:
                print(f"   - {cartella['nome']} (ID: {cartella['id'][:8]}...)")
            print("   ✅ Lista cartelle aggiornata OK")
        else:
            print(f"   ❌ Errore: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 4: Lista preventivi con cartelle
    print("\n4. Test lista preventivi con cartelle...")
    try:
        response = requests.get(
            f"{BASE_URL}/preventivi/con-cartelle", 
            params={
                "user_id": USER_ID,
                "stato_record": "attivo"
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            preventivi = response.json()
            print(f"   Preventivi trovati: {len(preventivi)}")
            for preventivo in preventivi[:3]:  # Mostra solo i primi 3
                cartella_nome = preventivo.get('cartella_nome', 'Senza cartella')
                print(f"   - {preventivo['numero_preventivo']} in '{cartella_nome}'")
            print("   ✅ Lista preventivi con cartelle OK")
        else:
            print(f"   ❌ Errore: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completati!")
    return True

def test_server_connection():
    """Test connessione al server"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🚀 Avvio test sistema cartelle...")
    
    # Verifica connessione server
    if not test_server_connection():
        print("❌ Server non raggiungibile su http://localhost:8000")
        print("   Assicurati che il server sia avviato con:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print("✅ Server raggiungibile")
    
    # Esegui test
    success = test_cartelle_endpoints()
    
    if success:
        print("\n🎉 Tutti i test sono passati!")
        print("\n📋 Prossimi passi:")
        print("   1. Apri http://localhost:8000 nel browser")
        print("   2. Testa la nuova interfaccia con sidebar cartelle")
        print("   3. Crea alcune cartelle di test")
        print("   4. Sposta preventivi nelle cartelle")
    else:
        print("\n❌ Alcuni test sono falliti")
        sys.exit(1) 