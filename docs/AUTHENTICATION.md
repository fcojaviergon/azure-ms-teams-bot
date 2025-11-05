# Guía de Autenticación y Modos de Operación

## 🔐 Autenticación en Microsoft Teams

### ¿Necesito implementar login de usuario?

**NO** - La autenticación de usuarios está **automáticamente resuelta por Microsoft Teams** a través de Microsoft Entra ID (anteriormente Azure AD).

### ¿Cómo funciona?

Cuando un usuario interactúa con el bot en Teams:

1. **Microsoft Teams autentica automáticamente al usuario** usando su cuenta de Microsoft 365
2. El bot recibe la identidad del usuario (ID, nombre, email) en cada mensaje
3. **No hay necesidad de crear un sistema de login separado**

### Identidad del usuario en el código

En el código del bot (`src/bot/teams_bot.py`), la identidad del usuario está disponible automáticamente:

```python
async def on_message_activity(self, turn_context: TurnContext):
    # Usuario ya autenticado por Teams
    user = turn_context.activity.from_property
    user_id = user.id          # ID único del usuario
    user_name = user.name      # Nombre del usuario

    # No necesitas solicitar login
```

### Autenticación del Bot con Azure

El bot se autentica con Azure Bot Service usando:
- `MICROSOFT_APP_ID` - ID de la aplicación del bot
- `MICROSOFT_APP_PASSWORD` - Contraseña/secreto del bot

Estas credenciales se configuran en el `.env` y permiten que el bot se comunique con Teams.

---

## 🎭 Modo Mock vs Modo Real (SAP Ariba)

El proyecto soporta dos modos de operación para la integración con SAP Ariba:

### 1. Modo Mock (Desarrollo) 🎭

**Recomendado para desarrollo local y pruebas**

#### Características:
- ✅ No requiere credenciales reales de SAP Ariba
- ✅ Datos simulados realistas (órdenes de compra, requisiciones, proveedores)
- ✅ Respuestas instantáneas sin llamadas HTTP
- ✅ Perfecto para desarrollo y demos
- ✅ No consume APIs reales

#### Configuración:
```bash
# .env
ARIBA_USE_MOCK=True

# Las credenciales de Ariba NO son necesarias en modo mock
# ARIBA_API_BASE_URL=  # No requerido
# ARIBA_API_KEY=       # No requerido
# ...
```

#### Datos Mock Incluidos:
- **3 proveedores** de ejemplo (Acme Corporation, Global Tech Solutions, Office Supplies Pro)
- **3 órdenes de compra** con diferentes estados (Approved, Pending, Delivered)
- **3 requisiciones de compra** en varios estados (Approved, Pending Approval, Draft)
- Datos en español con moneda EUR
- Búsqueda funcional por todos los documentos

#### Log de identificación:
```
🎭 Using MOCK Ariba service - get_purchase_orders
```

### 2. Modo Real (Producción) 🌐

**Para integración con SAP Ariba real**

#### Características:
- ✅ Conexión real con SAP Ariba API
- ✅ Autenticación OAuth2
- ✅ Datos en tiempo real
- ✅ Retry logic y manejo de errores
- ✅ Cache inteligente con Redis

#### Configuración:
```bash
# .env
ARIBA_USE_MOCK=False

# Credenciales reales de SAP Ariba (REQUERIDAS)
ARIBA_API_BASE_URL=https://openapi.ariba.com
ARIBA_API_KEY=your-actual-api-key
ARIBA_REALM=your-realm
ARIBA_CLIENT_ID=your-client-id
ARIBA_CLIENT_SECRET=your-client-secret
ARIBA_OAUTH_TOKEN_URL=https://api.ariba.com/v2/oauth/token
```

#### Log de identificación:
```
🌐 Initializing REAL Ariba service (live API)
```

---

## 🔄 Cambiar entre Modos

Para cambiar de modo, simplemente actualiza el `.env`:

```bash
# Cambiar a modo Mock
ARIBA_USE_MOCK=True

# Cambiar a modo Real
ARIBA_USE_MOCK=False
```

**No hay cambios de código necesarios** - el sistema automáticamente usa el servicio correcto.

---

## 🏗️ Arquitectura de Servicios

```
┌─────────────────────────────────────┐
│   src/services/ariba_factory.py     │
│   (Selecciona el servicio correcto) │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌──────────────┐    ┌───────────────────┐
│ MOCK Service │    │  REAL Service     │
│              │    │                   │
│ • Datos      │    │ • API HTTP        │
│   simulados  │    │ • OAuth2          │
│ • Sin red    │    │ • Cache Redis     │
│ • Instantáneo│    │ • Retry logic     │
└──────────────┘    └───────────────────┘
```

### Factory Pattern

El archivo `src/services/ariba_factory.py` implementa el patrón Factory:

```python
from src.services.ariba_factory import ariba

# 'ariba' es automáticamente el servicio correcto (mock o real)
orders = await ariba.get_purchase_orders()
```

---

## 📝 Uso en el Código

### Importar el servicio:

```python
# Usa el factory - automáticamente selecciona mock o real
from src.services.ariba_factory import ariba

# Ejemplo de uso
async def get_orders():
    # Funciona igual en modo mock y real
    response = await ariba.get_purchase_orders(
        filters={"status": "Approved"},
        page=1,
        page_size=10
    )
    return response.records
```

### No uses directamente:
```python
# ❌ NO hagas esto
from src.services.ariba_service import ariba_service

# ✅ Usa el factory
from src.services.ariba_factory import ariba
```

---

## 🧪 Testing

### Para desarrollo local:
```bash
# 1. Configura modo mock
ARIBA_USE_MOCK=True

# 2. No necesitas credenciales de Ariba
# 3. Ejecuta el bot
python run.py

# 4. El bot usará datos mock automáticamente
```

### Para testing en producción:
```bash
# 1. Configura modo real
ARIBA_USE_MOCK=False

# 2. Añade credenciales reales de Ariba
# 3. Ejecuta pruebas
python scripts/test_services.py
```

---

## 🔒 Seguridad

### Modo Mock:
- ✅ Seguro para desarrollo
- ✅ Sin credenciales sensibles necesarias
- ✅ Puede commitirse el .env con ARIBA_USE_MOCK=True

### Modo Real:
- ⚠️ **NUNCA** commites credenciales reales
- ⚠️ Usa Azure Key Vault en producción
- ⚠️ Variables de entorno para CI/CD

---

## 📊 Resumen Rápido

| Aspecto | Modo Mock 🎭 | Modo Real 🌐 |
|---------|-------------|-------------|
| **Uso** | Desarrollo local | Producción |
| **Credenciales Ariba** | No requeridas | Requeridas |
| **Datos** | Simulados | Tiempo real |
| **Velocidad** | Instantáneo | Depende de API |
| **Costos** | Gratis | Consume API |
| **Autenticación Usuario** | No necesaria (Teams) | No necesaria (Teams) |

---

## 🐛 Troubleshooting

### Error: `'access_token'` o errores de autenticación

**Síntoma**: El bot falla con un error relacionado con `access_token` cuando intenta enviar mensajes.

**Causa**: Credenciales del bot (MICROSOFT_APP_ID/PASSWORD) no configuradas o inválidas.

**Soluciones**:

#### Opción 1: Testing Local con Bot Framework Emulator (Recomendado para desarrollo)

Para desarrollo local sin configurar credenciales de Azure:

1. Descarga [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. En tu `.env`:
   ```bash
   MICROSOFT_APP_ID=
   MICROSOFT_APP_PASSWORD=
   # Dejar vacío para testing local
   ```
3. Ejecuta el bot: `python run.py`
4. Abre Bot Framework Emulator
5. Conecta a: `http://localhost:3978/api/messages`
6. **No** configures App ID ni Password en el emulator (déjalos vacíos)

✅ **Ventajas**: No necesitas Azure, perfecto para desarrollo y testing de funcionalidades

#### Opción 2: Usar credenciales de Azure Bot Service

Si quieres probar con Teams real:

1. Crea un Azure Bot Service en el [portal de Azure](https://portal.azure.com)
2. Obtén el App ID y Password/Secret
3. Configura en `.env`:
   ```bash
   MICROSOFT_APP_ID=tu-app-id-de-azure
   MICROSOFT_APP_PASSWORD=tu-password-de-azure
   ```
4. Configura el Bot en Azure con tu endpoint:
   - Para local: usa [ngrok](https://ngrok.com) → `ngrok http 3978`
   - Endpoint: `https://tu-url-ngrok.ngrok.io/api/messages`
5. Instala el bot en Teams desde Azure

### Error: "Bot credentials not configured"

**Síntoma**: El log muestra advertencias `⚠️ Bot credentials not configured` al iniciar.

**Solución**:
- **Para testing local**: Esto es normal, usa Bot Framework Emulator (ver Opción 1 arriba)
- **Para Teams real**: Configura las credenciales de Azure (ver Opción 2 arriba)

### El bot no responde en Teams

**Diagnóstico**:
1. Revisa los logs - busca mensajes de error
2. Verifica que el webhook/endpoint esté configurado correctamente en Azure
3. Si usas ngrok, verifica que:
   - ngrok está corriendo
   - La URL en Azure coincide con la URL de ngrok
4. Verifica que las credenciales en `.env` coincidan exactamente con las de Azure
5. Verifica que el bot esté instalado en tu equipo/chat de Teams

### Modo Mock no funciona

**Síntoma**: Errores al consultar datos de Ariba incluso con `ARIBA_USE_MOCK=True`

**Solución**:
1. Verifica que `.env` tenga: `ARIBA_USE_MOCK=True`
2. Reinicia el bot completamente
3. Busca en logs al iniciar: `🎭 Ariba MOCK mode enabled`
4. Si ves `🌐 Ariba REAL mode enabled`, revisa tu archivo `.env`

---

## ❓ Preguntas Frecuentes

### ¿Necesito configurar autenticación OAuth de usuarios?
**No**. Microsoft Teams ya autentica a los usuarios automáticamente via Microsoft Entra ID.

### ¿Necesito credenciales de Azure para testing local?
**No**. Usa Bot Framework Emulator (ver sección Troubleshooting arriba) para testing local sin credenciales.

### ¿Puedo usar el bot sin credenciales de SAP Ariba?
**Sí**. Usa `ARIBA_USE_MOCK=True` para desarrollo sin credenciales reales. Los datos mock incluyen proveedores, órdenes y requisiciones de ejemplo.

### ¿Cómo sé qué modo de Ariba estoy usando?
Revisa los logs al iniciar:
- `🎭 Ariba MOCK mode enabled` - Modo mock (desarrollo)
- `🌐 Ariba REAL mode enabled` - Modo real (producción)

### ¿Cómo sé si las credenciales del bot están configuradas?
Busca en los logs al iniciar:
- `✅ Bot credentials configured` - Credenciales OK
- `⚠️ Bot credentials not configured` - Sin credenciales (usa Emulator)

### ¿Los datos mock son realistas?
Sí, incluyen:
- 3 proveedores con datos completos
- 3 órdenes de compra con diferentes estados
- 3 requisiciones de compra
- Todo en español con moneda EUR

### ¿Puedo añadir más datos mock?
Sí, edita `src/services/ariba_mock_service.py` en el método `_init_mock_data()` y añade tus propios datos.

---

## 🚀 Inicio Rápido

```bash
# 1. Copia el .env.example
cp .env.example .env

# 2. Para desarrollo, deja el modo mock activo
# ARIBA_USE_MOCK=True (ya está por defecto)

# 3. Configura solo las credenciales de Teams
MICROSOFT_APP_ID=tu-app-id
MICROSOFT_APP_PASSWORD=tu-app-password

# 4. Ejecuta el bot
python run.py

# ✅ El bot funcionará con datos mock de Ariba
# ✅ No necesitas login de usuario (Teams lo hace)
```

---

## 📚 Más Información

- [Quickstart](../QUICKSTART.md) - Guía de inicio rápido
- [Installation](INSTALLATION.md) - Instalación completa
- [User Guide](USER_GUIDE.md) - Guía de usuario
