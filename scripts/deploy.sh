#!/bin/bash

# Script para desplegar el bot a Azure
# Uso: ./scripts/deploy.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Deployment del Teams Bot a Azure ===${NC}\n"

# Cargar variables desde .env si existe
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Solicitar información si no está en .env
if [ -z "$RESOURCE_GROUP" ]; then
    read -p "Resource Group: " RESOURCE_GROUP
fi

if [ -z "$WEB_APP_NAME" ]; then
    read -p "Web App Name (ej: sierra-bot-v2-webapp): " WEB_APP_NAME
fi

echo -e "\n${YELLOW}Método de deployment:${NC}"
echo "1. Azure Web App (directo desde código)"
echo "2. Docker + Azure Container Registry (recomendado)"
read -p "Selecciona opción (1 o 2): " DEPLOY_METHOD

if [ "$DEPLOY_METHOD" = "1" ]; then
    # Deployment directo
    echo -e "\n${GREEN}[1/2] Desplegando código a Azure Web App...${NC}"
    
    az webapp up \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --runtime PYTHON:3.12 \
        --sku B1 \
        --logs
    
    echo -e "\n${GREEN}[2/2] Configurando variables de entorno...${NC}"
    
    # Configurar variables de entorno desde .env
    if [ -f .env ]; then
        az webapp config appsettings set \
            --name "$WEB_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --settings \
                MICROSOFT_APP_ID="$MICROSOFT_APP_ID" \
                MICROSOFT_APP_PASSWORD="$MICROSOFT_APP_PASSWORD" \
                MICROSOFT_APP_TENANT_ID="$MICROSOFT_APP_TENANT_ID" \
                BOT_ID="$BOT_ID" \
                AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
                AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
                AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
                AZURE_SEARCH_ENDPOINT="$AZURE_SEARCH_ENDPOINT" \
                AZURE_SEARCH_API_KEY="$AZURE_SEARCH_API_KEY" \
                AZURE_SEARCH_INDEX_NAME="$AZURE_SEARCH_INDEX_NAME" \
                REDIS_HOST="$REDIS_HOST" \
                REDIS_PASSWORD="$REDIS_PASSWORD" \
                REDIS_PORT="$REDIS_PORT" \
                REDIS_SSL="$REDIS_SSL" \
                ARIBA_USE_MOCK="$ARIBA_USE_MOCK" \
                ENVIRONMENT="production" \
                LOG_LEVEL="INFO" \
                PORT="8000" \
            --output none
    fi
    
elif [ "$DEPLOY_METHOD" = "2" ]; then
    # Deployment con Docker
    
    if [ -z "$ACR_NAME" ]; then
        read -p "Azure Container Registry Name (ej: sierrabotv2acr): " ACR_NAME
    fi
    
    echo -e "\n${GREEN}[1/5] Verificando Azure Container Registry...${NC}"
    
    # Crear ACR si no existe
    if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
        echo -e "${YELLOW}Creando Azure Container Registry...${NC}"
        az acr create \
            --name "$ACR_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --sku Basic \
            --admin-enabled true
    fi
    
    echo -e "\n${GREEN}[2/5] Building y pushing imagen Docker...${NC}"
    
    # Build y push usando ACR
    az acr build \
        --registry "$ACR_NAME" \
        --image teams-bot:latest \
        --image teams-bot:$(date +%Y%m%d-%H%M%S) \
        --file Dockerfile \
        .
    
    echo -e "\n${GREEN}[3/5] Configurando Web App para usar container...${NC}"
    
    # Obtener credenciales del ACR
    ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
    ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)
    
    # Configurar Web App para usar el container
    az webapp config container set \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --docker-custom-image-name "${ACR_NAME}.azurecr.io/teams-bot:latest" \
        --docker-registry-server-url "https://${ACR_NAME}.azurecr.io" \
        --docker-registry-server-user "$ACR_USERNAME" \
        --docker-registry-server-password "$ACR_PASSWORD"
    
    echo -e "\n${GREEN}[4/5] Configurando variables de entorno...${NC}"
    
    # Configurar variables de entorno desde .env
    if [ -f .env ]; then
        az webapp config appsettings set \
            --name "$WEB_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --settings \
                MICROSOFT_APP_ID="$MICROSOFT_APP_ID" \
                MICROSOFT_APP_PASSWORD="$MICROSOFT_APP_PASSWORD" \
                MICROSOFT_APP_TENANT_ID="$MICROSOFT_APP_TENANT_ID" \
                BOT_ID="$BOT_ID" \
                AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
                AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
                AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
                AZURE_SEARCH_ENDPOINT="$AZURE_SEARCH_ENDPOINT" \
                AZURE_SEARCH_API_KEY="$AZURE_SEARCH_API_KEY" \
                AZURE_SEARCH_INDEX_NAME="$AZURE_SEARCH_INDEX_NAME" \
                REDIS_HOST="$REDIS_HOST" \
                REDIS_PASSWORD="$REDIS_PASSWORD" \
                REDIS_PORT="$REDIS_PORT" \
                REDIS_SSL="$REDIS_SSL" \
                ARIBA_USE_MOCK="$ARIBA_USE_MOCK" \
                ENVIRONMENT="production" \
                LOG_LEVEL="INFO" \
                PORT="8000" \
                WEBSITES_PORT="8000" \
            --output none
    fi
    
    echo -e "\n${GREEN}[5/5] Reiniciando Web App...${NC}"
    az webapp restart \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP"
    
else
    echo -e "${RED}Opción inválida${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Deployment completado!${NC}\n"

# Obtener URL del bot
BOT_URL="https://${WEB_APP_NAME}.azurewebsites.net"

echo -e "${YELLOW}=== INFORMACIÓN DEL DEPLOYMENT ===${NC}"
echo "Bot URL: $BOT_URL"
echo "Health Check: $BOT_URL/api/health"
echo "Messaging Endpoint: $BOT_URL/api/messages"
echo ""

# Verificar health
echo -e "${YELLOW}Verificando health endpoint...${NC}"
sleep 10  # Esperar a que el app inicie

if curl -f -s "$BOT_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ Bot está respondiendo correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Bot aún está iniciando. Verifica los logs:${NC}"
    echo "   az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
fi

echo ""
echo -e "${GREEN}Próximos pasos:${NC}"
echo "1. Verifica que el Bot Service tenga el endpoint correcto:"
echo "   Azure Portal → Bot Services → Configuration → Messaging endpoint"
echo "   Debe ser: $BOT_URL/api/messages"
echo ""
echo "2. Agrega el canal de Microsoft Teams:"
echo "   Azure Portal → Bot Services → Channels → Microsoft Teams"
echo ""
echo "3. Descarga el Teams App Package y publícalo en Teams"
echo ""
echo -e "${YELLOW}Ver logs en tiempo real:${NC}"
echo "   az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
