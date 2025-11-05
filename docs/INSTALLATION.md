# Guía de Instalación y Configuración

## Estado del Proyecto

### ✅ Completado
- Arquitectura modular en 3 capas
- Modelos de datos (Ariba, Conversación)
- Servicios de Azure (OpenAI, Cognitive Search)
- Integración SAP Ariba con OAuth2
- Sistema de caché Redis
- Logging y monitoreo
- Configuración con Pydantic

### 🚧 Pendiente de Implementar
- **Bot de Teams** (capa de conversación completa)
- **API REST** (aplicación Flask/aiohttp)
- **Docker** (Dockerfile y docker-compose)
- **CI/CD** (Azure DevOps pipelines)
- **IaC** (Bicep templates para infraestructura)
- **Tests** (unitarios e integración)
- **Scripts** de deployment

---

## Prerequisitos

### 1. Cuenta de Azure
- Suscripción activa de Azure
- Permisos para crear recursos

### 2. Herramientas Requeridas
```bash
# Python 3.9 o superior
python --version

# Azure CLI
az --version

# Git
git --version

# Docker (opcional, para desarrollo local)
docker --version
```

### 3. Recursos de Azure Necesarios

Antes de ejecutar el bot, necesitas crear estos recursos en Azure:

#### a) Azure Bot Service
```bash
# Crear un Bot Registration
az bot create \
  --resource-group <your-rg> \
  --name <bot-name> \
  --kind registration \
  --sku F0 \
  --appid <app-id> \
  --password <app-password>
```

#### b) Azure OpenAI
```bash
# Crear instancia de Azure OpenAI
az cognitiveservices account create \
  --name <openai-name> \
  --resource-group <your-rg> \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Desplegar modelo GPT-4
az cognitiveservices account deployment create \
  --name <openai-name> \
  --resource-group <your-rg> \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

#### c) Azure Cognitive Search
```bash
# Crear servicio de búsqueda
az search service create \
  --name <search-name> \
  --resource-group <your-rg> \
  --sku basic \
  --location eastus
```

#### d) Azure Redis Cache
```bash
# Crear instancia de Redis
az redis create \
  --name <redis-name> \
  --resource-group <your-rg> \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

#### e) Azure Key Vault (Recomendado)
```bash
# Crear Key Vault
az keyvault create \
  --name <keyvault-name> \
  --resource-group <your-rg> \
  --location eastus
```

---

## Instalación Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/fcojaviergon/azure-ms-teams-bot.git
cd azure-ms-teams-bot
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Configuración mínima requerida en `.env`:

```env
# Azure Bot Service
MICROSOFT_APP_ID=your-app-id-from-azure-portal
MICROSOFT_APP_PASSWORD=your-app-password
BOT_ID=your-bot-id

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Cognitive Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=ariba-knowledge

# Azure Redis Cache
REDIS_HOST=your-redis.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=your-redis-password
REDIS_SSL=True

# SAP Ariba Configuration
ARIBA_API_BASE_URL=https://openapi.ariba.com
ARIBA_API_KEY=your-ariba-api-key
ARIBA_REALM=your-realm
ARIBA_CLIENT_ID=your-client-id
ARIBA_CLIENT_SECRET=your-client-secret
ARIBA_OAUTH_TOKEN_URL=https://api.ariba.com/v2/oauth/token

# Application Insights (Opcional)
APPINSIGHTS_CONNECTION_STRING=your-connection-string
```

### 5. Obtener Credenciales

#### Azure Bot Service (App ID y Password)
1. Ve al Azure Portal
2. Navega a "Azure Active Directory" > "App registrations"
3. Crea o selecciona tu app registration
4. Copia el "Application (client) ID"
5. En "Certificates & secrets", crea un nuevo client secret
6. Copia el secret value inmediatamente (no se mostrará de nuevo)

#### Azure OpenAI
```bash
# Obtener endpoint
az cognitiveservices account show \
  --name <openai-name> \
  --resource-group <your-rg> \
  --query "properties.endpoint" -o tsv

# Obtener API key
az cognitiveservices account keys list \
  --name <openai-name> \
  --resource-group <your-rg> \
  --query "key1" -o tsv
```

#### Azure Cognitive Search
```bash
# Obtener admin key
az search admin-key show \
  --service-name <search-name> \
  --resource-group <your-rg> \
  --query "primaryKey" -o tsv
```

#### Redis Cache
```bash
# Obtener password
az redis list-keys \
  --name <redis-name> \
  --resource-group <your-rg> \
  --query "primaryKey" -o tsv
```

---

## Ejecución Local (Cuando esté completo)

⚠️ **NOTA**: La aplicación aún no está completa. Falta implementar:
- El bot de Teams
- La API REST
- Los endpoints HTTP

Una vez completado, podrás ejecutar:

```bash
# Opción 1: Ejecutar directamente con Python
python -m src.api.app

# Opción 2: Ejecutar con Docker (cuando esté disponible)
docker-compose up -d
```

---

## Configurar Bot en Teams

### 1. Crear App Package
1. Ve a [Teams Developer Portal](https://dev.teams.microsoft.com/)
2. Crea una nueva app
3. Configura:
   - **App ID**: El mismo de Azure Bot Service
   - **Bot endpoint**: `https://your-bot-url.azurewebsites.net/api/messages`
   - **Scopes**: Personal, Team, GroupChat

### 2. Instalar en Teams
1. Descarga el app package (.zip)
2. En Teams, ve a "Apps" > "Upload a custom app"
3. Selecciona el archivo .zip

---

## Crear Índice de Cognitive Search

Para que el bot pueda buscar información, necesitas crear un índice:

```python
# Script para crear índice (crear como scripts/create_search_index.py)
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.core.credentials import AzureKeyCredential

# Definir índice
index = SearchIndex(
    name="ariba-knowledge",
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="created_date", type=SearchFieldDataType.DateTimeOffset),
    ],
)

# Crear índice
client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
client.create_index(index)
```

---

## Testing

```bash
# Ejecutar tests unitarios (cuando estén disponibles)
pytest tests/unit

# Ejecutar tests de integración
pytest tests/integration

# Coverage
pytest --cov=src tests/
```

---

## Deployment a Azure

### Opción 1: Azure App Service

```bash
# Crear App Service Plan
az appservice plan create \
  --name <plan-name> \
  --resource-group <your-rg> \
  --sku B1 \
  --is-linux

# Crear Web App
az webapp create \
  --name <app-name> \
  --resource-group <your-rg> \
  --plan <plan-name> \
  --runtime "PYTHON:3.9"

# Deploy código
az webapp up \
  --name <app-name> \
  --resource-group <your-rg>
```

### Opción 2: Azure Container Instances (cuando Docker esté listo)

```bash
# Build y push a ACR
az acr build \
  --registry <acr-name> \
  --image teams-bot:latest .

# Deploy a ACI
az container create \
  --name teams-bot \
  --resource-group <your-rg> \
  --image <acr-name>.azurecr.io/teams-bot:latest \
  --dns-name-label teams-bot \
  --ports 3978
```

---

## Troubleshooting

### Error: "No module named 'src'"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: Redis connection failed
```bash
# Verificar conectividad
redis-cli -h <redis-host> -p 6380 -a <password> --tls ping
```

### Error: OpenAI authentication failed
```bash
# Verificar que el endpoint y key sean correctos
curl -H "api-key: $AZURE_OPENAI_API_KEY" \
  "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2023-05-15"
```

### Error: Bot not responding in Teams
1. Verificar que el endpoint esté público y accesible
2. Verificar que el App ID y Password sean correctos
3. Revisar logs en Application Insights
4. Verificar que el bot esté registrado en el canal de Teams

---

## Próximos Pasos

Para completar el MVP, se necesita implementar:

1. **Bot de Teams** (`src/bot/teams_bot.py`)
   - Handler de mensajes
   - Dialog management
   - Adaptive cards

2. **API REST** (`src/api/app.py`)
   - Endpoint `/api/messages` para Bot Framework
   - Health check endpoints
   - Webhooks para notificaciones

3. **Docker**
   - Dockerfile multi-stage
   - docker-compose.yml para desarrollo local

4. **CI/CD**
   - Azure DevOps pipeline para build
   - Pipeline para deployment
   - Tests automáticos

5. **Infrastructure as Code**
   - Templates Bicep para todos los recursos
   - Scripts de deployment automatizado

---

## Recursos Adicionales

- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/)
- [Teams Bot Development](https://docs.microsoft.com/microsoftteams/platform/bots/what-are-bots)
- [Azure OpenAI Service](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [SAP Ariba API Guide](https://help.sap.com/docs/ariba)

---

## Soporte

Para problemas o preguntas, contactar al equipo de desarrollo.
