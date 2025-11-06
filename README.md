# Azure MS Teams Bot with SAP Ariba Integration

Bot de Microsoft Teams con arquitectura nativa de Azure e integración con SAP Ariba.

## ✅ Estado del Proyecto

**🎉 MVP FUNCIONAL COMPLETO - LISTO PARA USAR 🎉**

### ✅ Implementado (MVP)
- ✅ Arquitectura modular en 3 capas (Conversación, Lógica, Datos)
- ✅ Bot de Microsoft Teams completo con Activity Handler
- ✅ API REST con aiohttp y endpoints de salud
- ✅ Azure OpenAI (GPT-4) para NLP e intenciones
- ✅ Azure Cognitive Search para búsqueda semántica
- ✅ Integración SAP Ariba con OAuth2 y retry logic
- ✅ **Modo Mock para desarrollo sin credenciales** 🎭
- ✅ Sistema de caché Redis con TTL
- ✅ Adaptive Cards para UI rica en Teams
- ✅ Dialog Manager para gestión de contexto
- ✅ Message Handler con routing de intenciones
- ✅ Sistema de logging con Application Insights
- ✅ Scripts de configuración y testing
- ✅ Documentación completa

### 🎯 Roadmap a Solución Empresarial

Este MVP es la base para evolucionar a una **Solución Empresarial Completa** con:

**🏢 Plan Completo Documentado** → Ver **[docs/ARCHITECTURE_PLAN.md](docs/ARCHITECTURE_PLAN.md)**

Incluye:
- 🏗️ Arquitectura objetivo completa (diagrama Mermaid)
- 📅 Plan de implementación por fases (10 fases, 26 semanas)
- 🔧 30+ tipos de consultas automatizadas
- 📊 Generación de reportes (PDF, Excel) y gráficos
- 🔔 Sistema de notificaciones y alertas
- 🌐 Interfaz web con autenticación
- ⚙️ Azure Functions + API Management
- 📈 Power BI Embedded
- 🤖 RPA con Power Automate
- 🛡️ Seguridad y cumplimiento normativo (Ley 19.628 Chile)
- 👨‍💼 Panel de administración completo
- 📚 Documentación y capacitación

### 🚧 Pendiente (MVP → Enterprise)
- ⏳ Expansión a 30+ tipos de consultas
- ⏳ Azure Functions (microservicios)
- ⏳ Generación de reportes PDF/Excel
- ⏳ Visualización de gráficos e indicadores
- ⏳ Sistema de notificaciones proactivas
- ⏳ Interfaz web (URL segura)
- ⏳ Power BI Embedded
- ⏳ Azure API Management
- ⏳ Panel de administración
- ⏳ RPA para sistemas sin API
- ⏳ Docker y docker-compose
- ⏳ Azure DevOps CI/CD pipelines
- ⏳ Infrastructure as Code (Bicep)
- ⏳ Tests unitarios e integración

**📖 Ver [docs/ARCHITECTURE_PLAN.md](docs/ARCHITECTURE_PLAN.md) para arquitectura, plan detallado y timeline**
**📖 Ver [docs/TODO.md](docs/TODO.md) para tareas específicas del MVP**

## ⚡ Inicio Rápido

```bash
# 1. Clonar y configurar
git clone https://github.com/fcojaviergon/azure-ms-teams-bot.git
cd azure-ms-teams-bot
./scripts/setup_local.sh

# 2. Configurar .env con tus credenciales
cp .env.example .env
nano .env

# 3. Modo Mock activado por defecto (sin credenciales de Ariba necesarias)
# ARIBA_USE_MOCK=True ya está configurado en .env.example

# 4. Probar conectividad
python scripts/test_services.py

# 5. Ejecutar el bot
./scripts/start_dev.sh
```

**👉 Ver [QUICKSTART.md](QUICKSTART.md) para instrucciones paso a paso completas.**

**💡 Para desarrollo sin credenciales de SAP Ariba, el modo mock está activado por defecto. Ver [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md).**

## Arquitectura

### Componentes Azure
- **Azure Bot Service**: Gestión de conversaciones con Teams
- **Azure OpenAI (GPT-4)**: Motor de procesamiento de lenguaje natural
- **Azure Cognitive Search**: Búsqueda inteligente de información
- **Azure API Management**: Gateway seguro para SAP Ariba
- **Azure Redis Cache**: Cache distribuido para optimización
- **Azure Key Vault**: Gestión segura de secretos
- **Azure Application Insights**: Monitoreo y telemetría

### Arquitectura en Capas

```
┌─────────────────────────────────────────────────┐
│           Microsoft Teams (Frontend)            │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Capa de Conversación (Bot Layer)        │
│  - Azure Bot Service                            │
│  - Teams Adapter                                │
│  - Dialog Management                            │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│           Capa Lógica (Business Layer)          │
│  - Azure OpenAI Service                         │
│  - Intent Recognition                           │
│  - Business Rules                               │
│  - Workflow Orchestration                       │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│            Capa de Datos (Data Layer)           │
│  - Azure Cognitive Search                       │
│  - SAP Ariba Integration                        │
│  - Azure Redis Cache                            │
│  - Azure Storage                                │
└─────────────────────────────────────────────────┘
```

## Estructura del Proyecto

```
.
├── src/
│   ├── bot/                    # Capa de conversación
│   │   ├── __init__.py
│   │   ├── teams_bot.py       # Bot principal de Teams
│   │   ├── dialog_manager.py  # Gestión de diálogos
│   │   └── message_handler.py # Procesamiento de mensajes
│   ├── services/               # Capa lógica
│   │   ├── __init__.py
│   │   ├── openai_service.py  # Integración Azure OpenAI
│   │   ├── search_service.py  # Azure Cognitive Search
│   │   ├── ariba_service.py   # Integración SAP Ariba
│   │   ├── cache_service.py   # Redis Cache
│   │   └── auth_service.py    # OAuth2 Authentication
│   ├── models/                 # Modelos de datos
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   └── ariba_models.py
│   ├── api/                    # API REST
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── config/                 # Configuración
│   │   ├── __init__.py
│   │   └── settings.py
│   └── utils/                  # Utilidades
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
├── tests/
│   ├── unit/
│   └── integration/
├── infrastructure/             # IaC (Bicep/ARM)
│   ├── main.bicep
│   ├── bot-service.bicep
│   ├── openai.bicep
│   ├── cognitive-search.bicep
│   └── api-management.bicep
├── .azure-pipelines/          # Azure DevOps CI/CD
│   ├── build.yml
│   └── deploy.yml
├── docs/                       # Documentación
├── scripts/                    # Scripts de utilidad
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Características Principales

### 1. Integración con Microsoft Teams
- Soporte completo para conversaciones
- Cards adaptativas para UI rica
- Comandos y menciones
- Notificaciones proactivas

### 2. Azure OpenAI (GPT-4)
- Procesamiento de lenguaje natural
- Comprensión de intenciones
- Generación de respuestas contextuales
- Extracción de entidades

### 3. Azure Cognitive Search
- Búsqueda semántica
- Índices personalizados
- Facetas y filtros
- Sugerencias y autocompletado

### 4. Integración SAP Ariba
- **Modo Mock** para desarrollo sin credenciales reales 🎭
- **Modo Real** con APIs REST/SOAP autorizadas 🌐
- Autenticación OAuth2
- Cache inteligente
- Rate limiting y retry logic
- Cambio entre modos mediante configuración

### 5. Escalabilidad y Modularidad
- Arquitectura de microservicios
- Separación de capas (conversación, lógica, datos)
- Fácil extensión con nuevos modelos
- Feedback loop para mejora continua

## 📚 Documentación

### Para Empezar (MVP)
- **[🚀 Quickstart](QUICKSTART.md)** - ¡Pon el bot en marcha en 10 minutos!
- **[🔐 Autenticación y Modos](docs/AUTHENTICATION.md)** - Guía de autenticación Teams/Entra y modo mock
- **[📖 Guía de Instalación](docs/INSTALLATION.md)** - Instrucciones detalladas de instalación y configuración
- **[👤 Guía de Usuario](docs/USER_GUIDE.md)** - Cómo usar el bot

### Evolución a Empresa (Enterprise)
- **[🏗️ Plan de Arquitectura Empresarial](docs/ARCHITECTURE_PLAN.md)** - **NUEVO** - Arquitectura completa, plan por fases (26 semanas), componentes técnicos, roadmap y entregables
- **[📋 Lista de Tareas MVP](docs/TODO.md)** - Roadmap y mejoras del MVP actual

## Requisitos Previos

- Python 3.9+
- Azure Subscription
- Microsoft Teams (licencia)
- SAP Ariba API credentials
- Docker (opcional)

## Configuración

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd azure-ms-teams-bot
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

4. **Desplegar infraestructura en Azure**
```bash
cd infrastructure
az deployment group create \
  --resource-group <your-rg> \
  --template-file main.bicep
```

5. **Probar conectividad**
```bash
source venv/bin/activate
python scripts/test_services.py
```

6. **Ejecutar localmente (desarrollo)**
```bash
# Opción 1: Script de desarrollo
./scripts/start_dev.sh

# Opción 2: Directamente
python run.py

# El bot estará disponible en http://localhost:3978
# Endpoint de mensajes: http://localhost:3978/api/messages
```

7. **Probar con Bot Framework Emulator**
- Descargar [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
- Conectar a `http://localhost:3978/api/messages`
- Usar tus credenciales MICROSOFT_APP_ID y MICROSOFT_APP_PASSWORD

## Deployment

### Azure DevOps
El proyecto incluye pipelines de CI/CD para Azure DevOps:
- `build.yml`: Build, tests y Docker image
- `deploy.yml`: Deploy a Azure App Service

### Manual
```bash
# Build Docker image
docker build -t teams-bot:latest .

# Push to Azure Container Registry
az acr login --name <your-acr>
docker tag teams-bot:latest <your-acr>.azurecr.io/teams-bot:latest
docker push <your-acr>.azurecr.io/teams-bot:latest

# Deploy to App Service
az webapp config container set \
  --name <your-app-service> \
  --resource-group <your-rg> \
  --docker-custom-image-name <your-acr>.azurecr.io/teams-bot:latest
```

## Testing

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# Coverage
pytest --cov=src tests/
```

## Monitoreo

- **Application Insights**: Telemetría y métricas
- **Log Analytics**: Logs centralizados
- **Alertas**: Configuradas en Azure Monitor

## Seguridad

- Credenciales en Azure Key Vault
- OAuth2 para SAP Ariba
- HTTPS/TLS enforcement
- RBAC en Azure
- Secret scanning en CI/CD
- Dependency scanning

## Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto del equipo]
