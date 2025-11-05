#!/bin/bash
# Script para iniciar el bot en modo desarrollo

set -e

echo "🚀 Iniciando Azure Teams Bot en modo desarrollo..."

# Verificar que estamos en el directorio correcto
if [ ! -f "run.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Error: Entorno virtual no encontrado. Ejecuta scripts/setup_local.sh primero"
    exit 1
fi

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Verificar .env
if [ ! -f ".env" ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "   Copia .env.example a .env y configura tus credenciales"
    exit 1
fi

# Establecer variables de desarrollo
export ENVIRONMENT=development
export DEBUG=True
export LOG_LEVEL=DEBUG

echo "✅ Configuración cargada"
echo ""
echo "El bot se iniciará en http://localhost:3978"
echo "Endpoint de mensajes: http://localhost:3978/api/messages"
echo ""
echo "Presiona Ctrl+C para detener el bot"
echo ""

# Ejecutar bot
python run.py
