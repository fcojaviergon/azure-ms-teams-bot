#!/bin/bash

# Script para crear todos los recursos de Azure necesarios para el bot
# Uso: ./scripts/setup_azure_resources.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configuración de Recursos Azure para Teams Bot ===${NC}\n"

# Solicitar información básica
read -p "Nombre del Resource Group (ej: rg-teams-bot): " RESOURCE_GROUP
read -p "Región de Azure (ej: eastus): " LOCATION
read -p "Prefijo para nombres de recursos (ej: mybot): " PREFIX

# Generar nombres de recursos
BOT_NAME="${PREFIX}-teams-bot"
OPENAI_NAME="${PREFIX}-openai"
SEARCH_NAME="${PREFIX}-search"
REDIS_NAME="${PREFIX}-redis"
KEYVAULT_NAME="${PREFIX}-kv"
APP_SERVICE_PLAN="${PREFIX}-plan"
WEB_APP_NAME="${PREFIX}-webapp"

echo -e "\n${YELLOW}Se crearán los siguientes recursos:${NC}"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - Bot Service: $BOT_NAME"
echo "  - Azure OpenAI: $OPENAI_NAME"
echo "  - Cognitive Search: $SEARCH_NAME"
echo "  - Redis Cache: $REDIS_NAME"
echo "  - Key Vault: $KEYVAULT_NAME"
echo "  - App Service Plan: $APP_SERVICE_PLAN"
echo "  - Web App: $WEB_APP_NAME"
echo ""

read -p "¿Continuar? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 1
fi

# 0. Registrar proveedores de recursos necesarios
echo -e "\n${GREEN}[0/8] Registrando proveedores de Azure...${NC}"
az provider register --namespace Microsoft.BotService --wait
az provider register --namespace Microsoft.CognitiveServices --wait
az provider register --namespace Microsoft.Search --wait
az provider register --namespace Microsoft.Cache --wait
az provider register --namespace Microsoft.KeyVault --wait
az provider register --namespace Microsoft.Web --wait
echo "✅ Proveedores registrados"

# 1. Crear Resource Group
echo -e "\n${GREEN}[1/8] Creando Resource Group...${NC}"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

# 2. Crear Azure AD App Registration para el Bot
echo -e "\n${GREEN}[2/8] Creando App Registration...${NC}"
APP_ID=$(az ad app create \
  --display-name "$BOT_NAME" \
  --query appId -o tsv)

echo "App ID creado: $APP_ID"

# Crear Client Secret
APP_PASSWORD=$(az ad app credential reset \
  --id "$APP_ID" \
  --query password -o tsv)

echo -e "${YELLOW}⚠️  GUARDA ESTE PASSWORD (no se mostrará de nuevo):${NC}"
echo "App Password: $APP_PASSWORD"

# 3. Crear Azure Bot Service
echo -e "\n${GREEN}[3/8] Creando Azure Bot Service...${NC}"
az bot create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$BOT_NAME" \
  --appid "$APP_ID" \
  --app-type SingleTenant \
  --tenant-id "$(az account show --query tenantId -o tsv)" \
  --endpoint "https://${WEB_APP_NAME}.azurewebsites.net/api/messages" \
  --sku F0 \
  --output table

# 4. Crear Azure OpenAI
echo -e "\n${GREEN}[4/8] Creando Azure OpenAI...${NC}"
az cognitiveservices account create \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --kind OpenAI \
  --sku S0 \
  --location "$LOCATION" \
  --yes \
  --output table

# Obtener endpoint y key de OpenAI
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.endpoint" -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "key1" -o tsv)

echo "OpenAI Endpoint: $OPENAI_ENDPOINT"

# Desplegar modelo GPT-4
echo -e "\n${YELLOW}Desplegando modelo GPT-4 Turbo...${NC}"
az cognitiveservices account deployment create \
  --name "$OPENAI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "turbo-2024-04-09" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard" \
  --output table 2>/dev/null || {
    echo "${YELLOW}Nota: Intentando con gpt-35-turbo como alternativa...${NC}"
    az cognitiveservices account deployment create \
      --name "$OPENAI_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --deployment-name gpt-35-turbo \
      --model-name gpt-35-turbo \
      --model-version "0125" \
      --model-format OpenAI \
      --sku-capacity 10 \
      --sku-name "Standard" \
      --output table || echo "${RED}⚠️  No se pudo desplegar modelo. Configúralo manualmente después.${NC}"
  }

# 5. Crear Azure Cognitive Search
echo -e "\n${GREEN}[5/8] Creando Azure Cognitive Search...${NC}"
az search service create \
  --name "$SEARCH_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --sku basic \
  --location "$LOCATION" \
  --output table

# Obtener Search Key
SEARCH_KEY=$(az search admin-key show \
  --service-name "$SEARCH_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryKey" -o tsv)

SEARCH_ENDPOINT="https://${SEARCH_NAME}.search.windows.net"

# 6. Crear Azure Redis Cache
echo -e "\n${GREEN}[6/8] Creando Azure Redis Cache...${NC}"
az redis create \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Basic \
  --vm-size c0 \
  --output table

# Obtener Redis password
REDIS_PASSWORD=$(az redis list-keys \
  --name "$REDIS_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryKey" -o tsv)

REDIS_HOST="${REDIS_NAME}.redis.cache.windows.net"

# 7. Crear Azure Key Vault
echo -e "\n${GREEN}[7/8] Creando Azure Key Vault...${NC}"
az keyvault create \
  --name "$KEYVAULT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

KEYVAULT_URL="https://${KEYVAULT_NAME}.vault.azure.net/"

# Guardar secretos en Key Vault
echo -e "\n${YELLOW}Guardando secretos en Key Vault...${NC}"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "MicrosoftAppId" --value "$APP_ID" --output none
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "MicrosoftAppPassword" --value "$APP_PASSWORD" --output none
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "AzureOpenAIKey" --value "$OPENAI_KEY" --output none
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "AzureSearchKey" --value "$SEARCH_KEY" --output none
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "RedisPassword" --value "$REDIS_PASSWORD" --output none

# 8. Crear App Service Plan y Web App
echo -e "\n${GREEN}[8/8] Creando App Service...${NC}"
az appservice plan create \
  --name "$APP_SERVICE_PLAN" \
  --resource-group "$RESOURCE_GROUP" \
  --sku B1 \
  --is-linux \
  --output table

az webapp create \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --plan "$APP_SERVICE_PLAN" \
  --runtime "PYTHON:3.9" \
  --output table

# Configurar variables de entorno en Web App
echo -e "\n${YELLOW}Configurando variables de entorno en Web App...${NC}"
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    MICROSOFT_APP_ID="$APP_ID" \
    MICROSOFT_APP_PASSWORD="$APP_PASSWORD" \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$OPENAI_KEY" \
    AZURE_SEARCH_ENDPOINT="$SEARCH_ENDPOINT" \
    AZURE_SEARCH_API_KEY="$SEARCH_KEY" \
    REDIS_HOST="$REDIS_HOST" \
    REDIS_PASSWORD="$REDIS_PASSWORD" \
    AZURE_KEY_VAULT_URL="$KEYVAULT_URL" \
  --output none

# Generar archivo .env local
echo -e "\n${GREEN}Generando archivo .env.local...${NC}"
cat > .env.local << EOF
# Azure Bot Service
MICROSOFT_APP_ID=$APP_ID
MICROSOFT_APP_PASSWORD=$APP_PASSWORD
BOT_ID=$BOT_NAME

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Cognitive Search
AZURE_SEARCH_ENDPOINT=$SEARCH_ENDPOINT
AZURE_SEARCH_API_KEY=$SEARCH_KEY
AZURE_SEARCH_INDEX_NAME=ariba-knowledge

# Azure Key Vault
AZURE_KEY_VAULT_URL=$KEYVAULT_URL

# Azure Redis Cache
REDIS_HOST=$REDIS_HOST
REDIS_PORT=6380
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_SSL=True

# SAP Ariba Configuration (debes configurar estos valores manualmente)
ARIBA_API_BASE_URL=https://openapi.ariba.com
ARIBA_API_KEY=your-ariba-api-key
ARIBA_REALM=your-realm
ARIBA_CLIENT_ID=your-client-id
ARIBA_CLIENT_SECRET=your-client-secret
ARIBA_OAUTH_TOKEN_URL=https://api.ariba.com/v2/oauth/token

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=False
PORT=3978

# Cache Settings
CACHE_TTL_SECONDS=3600
CACHE_ENABLED=True

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Feature Flags
ENABLE_FEEDBACK_LOOP=True
ENABLE_ANALYTICS=True
ENABLE_PROACTIVE_NOTIFICATIONS=False
EOF

echo -e "\n${GREEN}✅ ¡Recursos creados exitosamente!${NC}\n"

echo -e "${YELLOW}=== RESUMEN DE RECURSOS ===${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Bot Name: $BOT_NAME"
echo "App ID: $APP_ID"
echo "Web App URL: https://${WEB_APP_NAME}.azurewebsites.net"
echo ""
echo -e "${YELLOW}=== CREDENCIALES ===${NC}"
echo "Todas las credenciales se han guardado en:"
echo "  - Key Vault: $KEYVAULT_NAME"
echo "  - Archivo local: .env.local"
echo ""
echo -e "${RED}⚠️  IMPORTANTE: Copia .env.local a .env y configura las credenciales de SAP Ariba${NC}"
echo ""
echo -e "${GREEN}Próximos pasos:${NC}"
echo "1. cp .env.local .env"
echo "2. Edita .env y agrega tus credenciales de SAP Ariba"
echo "3. Ejecuta: pip install -r requirements.txt"
echo "4. Crea el índice de Cognitive Search: python scripts/create_search_index.py"
echo "5. Despliega el bot: az webapp up --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
