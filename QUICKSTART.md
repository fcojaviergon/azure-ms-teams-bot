# 🚀 Quickstart Guide

Guía rápida para poner en marcha el bot en 10 minutos.

## Prerequisitos

- Python 3.9+
- Cuenta de Azure con los recursos creados
- Credenciales de SAP Ariba

## Paso 1: Clonar y Configurar

```bash
# Clonar el repositorio
git clone https://github.com/fcojaviergon/azure-ms-teams-bot.git
cd azure-ms-teams-bot

# Ejecutar script de configuración
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

## Paso 2: Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```bash
# Editar .env
nano .env
```

**Variables mínimas requeridas:**

```env
# Azure Bot Service
MICROSOFT_APP_ID=your-app-id
MICROSOFT_APP_PASSWORD=your-app-password
BOT_ID=your-bot-id

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Cognitive Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=ariba-knowledge

# Azure Redis Cache
REDIS_HOST=your-redis.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=your-password
REDIS_SSL=True

# SAP Ariba
ARIBA_API_BASE_URL=https://openapi.ariba.com
ARIBA_API_KEY=your-key
ARIBA_REALM=your-realm
ARIBA_CLIENT_ID=your-client-id
ARIBA_CLIENT_SECRET=your-secret
ARIBA_OAUTH_TOKEN_URL=https://api.ariba.com/v2/oauth/token
```

## Paso 3: Probar Conectividad

```bash
# Activar entorno virtual
source venv/bin/activate

# Probar servicios
python scripts/test_services.py
```

Deberías ver:
```
✅ Redis: Connected
✅ Ariba: OAuth2 token obtained
✅ OpenAI: Connected and responding
✅ Cognitive Search: Connected
```

## Paso 4: Ejecutar el Bot Localmente

```bash
# Iniciar el bot
./scripts/start_dev.sh

# O directamente:
python run.py
```

El bot estará disponible en: `http://localhost:3978`

## Paso 5: Probar el Bot

### Opción A: Bot Framework Emulator (Recomendado para desarrollo)

1. Descarga [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. Abre el emulator
3. Conecta a: `http://localhost:3978/api/messages`
4. Ingresa tu `MICROSOFT_APP_ID` y `MICROSOFT_APP_PASSWORD`
5. ¡Empieza a chatear!

### Opción B: Ngrok + Teams (Para probar en Teams)

```bash
# Instalar ngrok
# https://ngrok.com/download

# Exponer el bot
ngrok http 3978

# Usar la URL de ngrok (ej: https://abc123.ngrok.io)
# en el Bot Framework Portal como endpoint
```

## Paso 6: Registrar en Teams

1. Ve al [Azure Portal](https://portal.azure.com)
2. Busca tu Bot Service
3. En "Channels", agrega "Microsoft Teams"
4. En Teams, busca tu bot por nombre
5. ¡Empieza a chatear!

## Comandos de Prueba

Una vez conectado, prueba estos comandos:

```
/ayuda
```
Muestra el mensaje de bienvenida y ayuda.

```
Lista los últimos purchase orders
```
Muestra los últimos POs de Ariba.

```
Muéstrame el PO PO1234567
```
Busca un PO específico (reemplaza con un ID real).

```
¿Qué proveedores tenemos activos?
```
Lista proveedores activos.

```
/status
```
Verifica el estado del bot y servicios.

## Health Checks

El bot expone varios endpoints de salud:

```bash
# Health básico
curl http://localhost:3978/api/health

# Readiness (dependencias)
curl http://localhost:3978/api/health/ready

# Liveness
curl http://localhost:3978/api/health/live

# Info del bot
curl http://localhost:3978/
```

## Troubleshooting

### Error: "No module named 'src'"
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python run.py
```

### Error: "Redis connection failed"
Verifica que Redis esté corriendo y las credenciales sean correctas:
```bash
redis-cli -h your-redis.redis.cache.windows.net -p 6380 -a your-password --tls ping
```

### Error: "Bot not responding"
1. Verifica que el endpoint esté correcto en Azure Portal
2. Verifica que ngrok esté corriendo (si aplica)
3. Revisa los logs del bot

### Error: "OpenAI authentication failed"
Verifica las credenciales:
```bash
curl -H "api-key: $AZURE_OPENAI_API_KEY" \
  "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2023-05-15"
```

## Detener el Bot

```bash
# Si está corriendo en terminal:
Ctrl + C

# Si está en background:
pkill -f "python run.py"
```

## Próximos Pasos

- ✅ Bot funcionando localmente
- 📖 Lee la [Guía de Usuario](docs/USER_GUIDE.md)
- 🚀 [Deploy a Azure](docs/INSTALLATION.md#deployment-a-azure)
- 🧪 Ejecuta los tests: `pytest tests/`
- 🐳 Usa Docker: Ver [TODO.md](docs/TODO.md)

## Recursos

- [Documentación Completa](docs/INSTALLATION.md)
- [Arquitectura](README.md#arquitectura)
- [Tareas Pendientes](docs/TODO.md)
- [Azure Bot Service Docs](https://docs.microsoft.com/azure/bot-service/)
- [Teams Bot Development](https://docs.microsoft.com/microsoftteams/platform/bots/what-are-bots)

## ¿Problemas?

Si encuentras problemas:
1. Revisa los logs en la consola
2. Ejecuta `python scripts/test_services.py`
3. Verifica el archivo `.env`
4. Consulta la [documentación completa](docs/INSTALLATION.md)

---

**¡Listo! 🎉** Ahora tienes el bot funcionando localmente y puedes empezar a integrarlo con Teams.
