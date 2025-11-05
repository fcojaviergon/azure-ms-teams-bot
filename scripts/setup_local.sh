#!/bin/bash
# Script para configurar el entorno local de desarrollo

set -e

echo "🚀 Configurando entorno local para Azure Teams Bot..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION instalado${NC}"

# Crear entorno virtual
echo -e "${YELLOW}Creando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${YELLOW}⚠️  Entorno virtual ya existe${NC}"
fi

# Activar entorno virtual
echo -e "${YELLOW}Activando entorno virtual...${NC}"
source venv/bin/activate

# Actualizar pip
echo -e "${YELLOW}Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
echo -e "${YELLOW}Instalando dependencias...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Verificar archivo .env
echo -e "${YELLOW}Verificando configuración...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado desde .env.example${NC}"
    echo -e "${YELLOW}⚠️  Por favor edita .env con tus credenciales antes de ejecutar el bot${NC}"
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
fi

# Crear directorios necesarios
echo -e "${YELLOW}Creando directorios...${NC}"
mkdir -p logs
mkdir -p tmp
echo -e "${GREEN}✅ Directorios creados${NC}"

echo ""
echo -e "${GREEN}🎉 ¡Configuración completada!${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Edita .env con tus credenciales de Azure"
echo "2. Ejecuta: source venv/bin/activate"
echo "3. Ejecuta: python run.py"
echo ""
