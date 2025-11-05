# Azure MS Teams Bot with SAP Ariba Integration

Bot de Microsoft Teams con arquitectura nativa de Azure e integración con SAP Ariba.

## ⚠️ Estado del Proyecto

**🚧 TRABAJO EN PROGRESO - MVP PARCIALMENTE COMPLETO 🚧**

### ✅ Implementado (Fase 1)
- ✅ Arquitectura modular en 3 capas
- ✅ Servicios de Azure OpenAI (GPT-4)
- ✅ Servicios de Azure Cognitive Search
- ✅ Integración SAP Ariba con OAuth2
- ✅ Sistema de caché Redis
- ✅ Modelos de datos y configuración
- ✅ Documentación de instalación y uso

### 🚧 Pendiente (Fase 2)
- ❌ Bot de Teams (capa de conversación)
- ❌ API REST (endpoints HTTP)
- ❌ Docker y docker-compose
- ❌ Azure DevOps CI/CD pipelines
- ❌ Infrastructure as Code (Bicep)
- ❌ Tests unitarios e integración

**📖 Para más detalles sobre lo que falta, ver: [docs/TODO.md](docs/TODO.md)**

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
- APIs REST/SOAP autorizadas
- Autenticación OAuth2
- Cache inteligente
- Rate limiting y retry logic

### 5. Escalabilidad y Modularidad
- Arquitectura de microservicios
- Separación de capas (conversación, lógica, datos)
- Fácil extensión con nuevos modelos
- Feedback loop para mejora continua

## 📚 Documentación

- **[Guía de Instalación](docs/INSTALLATION.md)** - Instrucciones detalladas de instalación y configuración
- **[Guía de Usuario](docs/USER_GUIDE.md)** - Cómo usar el bot (cuando esté completo)
- **[Lista de Tareas](docs/TODO.md)** - Tareas pendientes y plan de implementación

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

5. **Ejecutar localmente (desarrollo)**
```bash
# ⚠️ PENDIENTE: El bot aún no está implementado
# Cuando esté completo:
python -m src.api.app
```

6. **Ejecutar con Docker**
```bash
# ⚠️ PENDIENTE: Docker aún no está configurado
# Cuando esté completo:
docker-compose up -d
```

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
