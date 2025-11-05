# Lista de Tareas Pendientes

## 🎯 Estado Actual del Proyecto

### ✅ Completado (Fase 1)
- [x] Estructura modular del proyecto (capas: conversación, lógica, datos)
- [x] Modelos de datos Pydantic para Ariba y conversaciones
- [x] Servicio Azure OpenAI (GPT-4) con generación de respuestas e intent extraction
- [x] Servicio Azure Cognitive Search con búsqueda semántica
- [x] Servicio SAP Ariba con OAuth2, retry logic y cache
- [x] Servicio de Cache (Redis) con TTL y patterns
- [x] Servicio de Autenticación OAuth2 para Ariba
- [x] Sistema de logging con Application Insights
- [x] Configuración con Pydantic Settings
- [x] Validadores de entrada
- [x] Documentación básica (README, Installation Guide, User Guide)

---

## 🚧 Pendiente de Implementar (Fase 2)

### 1. Capa de Conversación - Bot de Teams
**Prioridad: ALTA** - El bot no puede funcionar sin esto

#### Archivos a crear:
- [ ] `src/bot/__init__.py`
- [ ] `src/bot/teams_bot.py` - Bot principal con Teams adapter
- [ ] `src/bot/dialog_manager.py` - Gestión de diálogos y contexto
- [ ] `src/bot/message_handler.py` - Procesamiento de mensajes
- [ ] `src/bot/cards.py` - Adaptive Cards para Teams
- [ ] `src/bot/activity_handler.py` - Handler de actividades del Bot Framework

#### Funcionalidades requeridas:
```python
# teams_bot.py debe incluir:
- TeamsActivityHandler para manejar eventos de Teams
- Integración con Azure Bot Service
- Manejo de mensajes (texto, menciones, comandos)
- Manejo de eventos (conversationUpdate, messageReaction)
- Envío de Adaptive Cards
- Manejo de errores y logging
```

#### Dependencias:
```python
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount
from botbuilder.integration.aiohttp import CloudAdapter
```

---

### 2. API REST Application
**Prioridad: ALTA** - Necesaria para recibir mensajes de Teams

#### Archivos a crear:
- [ ] `src/api/__init__.py`
- [ ] `src/api/app.py` - Aplicación principal (Flask o aiohttp)
- [ ] `src/api/routes.py` - Endpoints REST
- [ ] `src/api/middleware.py` - Middleware de autenticación y logging
- [ ] `src/api/health.py` - Health checks

#### Endpoints requeridos:
```python
POST /api/messages          # Endpoint principal del Bot Framework
GET  /api/health           # Health check
GET  /api/health/ready     # Readiness probe
GET  /api/health/live      # Liveness probe
POST /api/webhooks/ariba   # Webhooks de Ariba (opcional)
```

#### Estructura sugerida (aiohttp):
```python
from aiohttp import web
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

async def messages(req: web.Request) -> web.Response:
    """Endpoint principal para Bot Framework"""
    return await adapter.process(req)

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/api/health", health_check)
```

---

### 3. Docker y Containerización
**Prioridad: MEDIA** - Facilita deployment

#### Archivos a crear:
- [ ] `Dockerfile` - Multi-stage build
- [ ] `docker-compose.yml` - Para desarrollo local
- [ ] `.dockerignore` - Excluir archivos innecesarios

#### Dockerfile sugerido:
```dockerfile
# Stage 1: Build
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 3978
CMD ["python", "-m", "src.api.app"]
```

#### docker-compose.yml sugerido:
```yaml
version: '3.8'
services:
  bot:
    build: .
    ports:
      - "3978:3978"
    env_file: .env
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

### 4. Azure DevOps CI/CD
**Prioridad: MEDIA** - Importante para deployment automatizado

#### Archivos a crear:
- [ ] `.azure-pipelines/build.yml` - Pipeline de build
- [ ] `.azure-pipelines/deploy.yml` - Pipeline de deployment
- [ ] `.azure-pipelines/test.yml` - Pipeline de tests

#### build.yml sugerido:
```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.9'

          - script: |
              pip install -r requirements.txt
              pytest tests/ --cov=src
            displayName: 'Install dependencies and run tests'

          - task: Docker@2
            inputs:
              command: buildAndPush
              repository: $(imageRepository)
              dockerfile: Dockerfile
              tags: |
                $(Build.BuildId)
                latest
```

---

### 5. Infrastructure as Code (IaC)
**Prioridad: MEDIA** - Para deployment consistente

#### Archivos a crear:
- [ ] `infrastructure/main.bicep` - Template principal
- [ ] `infrastructure/modules/bot-service.bicep`
- [ ] `infrastructure/modules/app-service.bicep`
- [ ] `infrastructure/modules/openai.bicep`
- [ ] `infrastructure/modules/cognitive-search.bicep`
- [ ] `infrastructure/modules/redis-cache.bicep`
- [ ] `infrastructure/modules/key-vault.bicep`
- [ ] `infrastructure/modules/api-management.bicep`
- [ ] `infrastructure/parameters/dev.json`
- [ ] `infrastructure/parameters/prod.json`

#### main.bicep estructura:
```bicep
targetScope = 'resourceGroup'

@description('Environment name')
param environment string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

// Bot Service
module botService 'modules/bot-service.bicep' = {
  name: 'botServiceDeployment'
  params: {
    botName: 'teams-ariba-bot-${environment}'
    location: location
  }
}

// OpenAI
module openai 'modules/openai.bicep' = {
  name: 'openaiDeployment'
  params: {
    name: 'openai-${environment}'
    location: location
  }
}

// Cognitive Search
module search 'modules/cognitive-search.bicep' = {
  name: 'searchDeployment'
  params: {
    name: 'search-${environment}'
    location: location
  }
}

// Redis Cache
module redis 'modules/redis-cache.bicep' = {
  name: 'redisDeployment'
  params: {
    name: 'redis-${environment}'
    location: location
  }
}
```

---

### 6. Tests
**Prioridad: MEDIA** - Importante para calidad

#### Archivos a crear:
- [ ] `tests/__init__.py`
- [ ] `tests/conftest.py` - Fixtures compartidos
- [ ] `tests/unit/test_openai_service.py`
- [ ] `tests/unit/test_ariba_service.py`
- [ ] `tests/unit/test_search_service.py`
- [ ] `tests/unit/test_cache_service.py`
- [ ] `tests/unit/test_auth_service.py`
- [ ] `tests/unit/test_models.py`
- [ ] `tests/integration/test_bot_flow.py`
- [ ] `tests/integration/test_ariba_integration.py`

#### Ejemplo de test:
```python
# tests/unit/test_openai_service.py
import pytest
from unittest.mock import AsyncMock, patch
from src.services.openai_service import openai_service

@pytest.mark.asyncio
async def test_generate_response():
    with patch.object(openai_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content="Test response"))]
        )

        response = await openai_service.generate_response("Hello")
        assert response == "Test response"
```

---

### 7. Scripts de Utilidad
**Prioridad: BAJA** - Útiles pero no críticos

#### Archivos a crear:
- [ ] `scripts/setup_azure_resources.sh` - Script para crear recursos
- [ ] `scripts/create_search_index.py` - Crear índice de búsqueda
- [ ] `scripts/test_ariba_connection.py` - Test de conexión a Ariba
- [ ] `scripts/load_sample_data.py` - Cargar datos de prueba
- [ ] `scripts/deploy.sh` - Script de deployment manual

---

### 8. Documentación Adicional
**Prioridad: BAJA**

#### Archivos a crear:
- [ ] `docs/ARCHITECTURE.md` - Arquitectura detallada
- [ ] `docs/API.md` - Documentación de API
- [ ] `docs/CONTRIBUTING.md` - Guía de contribución
- [ ] `docs/CHANGELOG.md` - Historial de cambios
- [ ] `docs/SECURITY.md` - Políticas de seguridad

---

## 📋 Plan de Implementación Sugerido

### Sprint 1 (Semana 1) - MVP Funcional
1. ✅ Implementar Bot de Teams básico
2. ✅ Implementar API REST con endpoint /api/messages
3. ✅ Integrar bot con servicios existentes
4. ✅ Test manual en Teams

### Sprint 2 (Semana 2) - Containerización
1. ✅ Crear Dockerfile
2. ✅ Crear docker-compose para desarrollo
3. ✅ Test de deployment local con Docker

### Sprint 3 (Semana 3) - CI/CD y IaC
1. ✅ Implementar pipelines de Azure DevOps
2. ✅ Crear templates Bicep
3. ✅ Deploy a ambiente de desarrollo

### Sprint 4 (Semana 4) - Tests y Refinamiento
1. ✅ Escribir tests unitarios
2. ✅ Escribir tests de integración
3. ✅ Refinar documentación
4. ✅ Deploy a producción

---

## 🎯 Criterios de Aceptación del MVP

Para considerar el MVP completo, debe cumplir:

### Funcionales
- [ ] Bot responde a mensajes en Teams
- [ ] Bot puede consultar Purchase Orders de Ariba
- [ ] Bot puede consultar Purchase Requisitions
- [ ] Bot puede buscar proveedores
- [ ] Bot usa Azure OpenAI para entender intenciones
- [ ] Bot usa Cognitive Search para buscar información
- [ ] Bot cachea respuestas para optimizar rendimiento

### Técnicos
- [ ] Aplicación corre en Docker
- [ ] Deployment automatizado con Azure DevOps
- [ ] Infraestructura desplegada con IaC (Bicep)
- [ ] Logs en Application Insights
- [ ] Health checks funcionando
- [ ] Tests con >70% coverage

### No Funcionales
- [ ] Tiempo de respuesta < 3 segundos
- [ ] Disponibilidad > 99%
- [ ] Autenticación OAuth2 funcionando
- [ ] Secrets en Key Vault
- [ ] Documentación completa

---

## 🔧 Comandos Útiles para Continuar

```bash
# Crear estructura de bot
mkdir -p src/bot tests/unit/bot tests/integration

# Crear estructura de API
mkdir -p src/api

# Crear estructura de infraestructura
mkdir -p infrastructure/modules infrastructure/parameters

# Crear estructura de CI/CD
mkdir -p .azure-pipelines

# Crear estructura de scripts
mkdir -p scripts

# Instalar dependencias adicionales que faltan
pip install botbuilder-core botbuilder-schema botbuilder-integration-aiohttp

# Ejecutar tests (cuando existan)
pytest tests/ -v --cov=src
```

---

## 📞 Próximos Pasos

¿Quieres que implemente alguna de estas partes? Puedo empezar por:

1. **Bot de Teams** (lo más crítico)
2. **API REST** (necesaria para el bot)
3. **Docker** (para facilitar deployment)
4. **Tests** (para asegurar calidad)
5. **IaC** (para deployment automatizado)

Indica cuál prefieres y continuamos con la implementación.
