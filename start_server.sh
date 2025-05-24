#!/bin/bash
# Script per avviare l'applicazione con tutte le configurazioni necessarie

echo "🚀 Avvio App Preventivi..."

# Configura le variabili d'ambiente per WeasyPrint
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:/usr/local/lib:$DYLD_LIBRARY_PATH"

# Attiva l'ambiente virtuale
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtuale attivato"
else
    echo "❌ Cartella venv non trovata. Assicurati di essere nella directory del progetto."
    exit 1
fi

# Verifica che WeasyPrint funzioni
python -c "import weasyprint; print('✅ WeasyPrint verificato')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ WeasyPrint non funziona correttamente"
    echo "💡 Prova a eseguire: brew install pango gdk-pixbuf libffi"
    exit 1
fi

echo "🔧 Configurazione completata"
echo "🌐 Avvio server su http://localhost:8000"
echo "📋 Ctrl+C per fermare il server"
echo ""

# Avvia il server FastAPI
python -m uvicorn app.main:app --reload --port 8000 