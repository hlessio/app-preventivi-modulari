#!/bin/bash
# Script per configurare l'ambiente per WeasyPrint su macOS

echo "🔧 Configurazione ambiente WeasyPrint..."

# Imposta le variabili d'ambiente per WeasyPrint
# Aggiungi percorsi specifici per glib e altre dipendenze
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/glib/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/glib/lib:/usr/local/lib:$DYLD_LIBRARY_PATH"

# Aggiungi anche i percorsi per altre dipendenze comuni di WeasyPrint
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/pango/lib:/opt/homebrew/opt/gdk-pixbuf/lib:/opt/homebrew/opt/libffi/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/opt/pango/lib/pkgconfig:/opt/homebrew/opt/gdk-pixbuf/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"

# Attiva l'ambiente virtuale
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtuale attivato"
else
    echo "❌ Cartella venv non trovata. Assicurati di essere nella directory del progetto."
    exit 1
fi

# Testa se WeasyPrint funziona
python -c "import weasyprint; print('✅ WeasyPrint importato correttamente')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ WeasyPrint configurato correttamente"
else
    echo "❌ Errore nella configurazione di WeasyPrint"
    echo "💡 Assicurati che le dipendenze siano installate:"
    echo "   brew install pango gdk-pixbuf libffi glib"
fi

echo "🚀 Ambiente pronto! Ora puoi avviare il server con:"
echo "   python -m uvicorn app.main:app --reload --port 8000" 