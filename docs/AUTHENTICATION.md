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

## ❓ Preguntas Frecuentes

### ¿Necesito configurar autenticación OAuth de usuarios?
**No**. Microsoft Teams ya autentica a los usuarios automáticamente.

### ¿Puedo usar el bot sin credenciales de SAP Ariba?
**Sí**. Usa `ARIBA_USE_MOCK=True` para desarrollo sin credenciales reales.

### ¿Cómo sé qué modo estoy usando?
Revisa los logs al iniciar - verás 🎭 para mock o 🌐 para real.

### ¿Los datos mock son realistas?
Sí, incluyen órdenes de compra, proveedores y requisiciones con datos completos en español.

### ¿Puedo añadir más datos mock?
Sí, edita `src/services/ariba_mock_service.py` en el método `_init_mock_data()`.

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
