# Actualización de Stack Tecnológico - FastAPI y PostgreSQL

## 🔄 Cambios de Stack Tecnológico

### Decisiones Arquitectónicas Actualizadas

Basado en feedback y mejores prácticas modernas, se han actualizado dos componentes clave:

#### 1. **FastAPI en lugar de aiohttp**
#### 2. **PostgreSQL con pgvector en lugar de Cosmos DB**

---

## 🚀 FastAPI vs aiohttp

### ¿Por qué FastAPI?

| Aspecto | aiohttp | FastAPI | Ganador |
|---------|---------|---------|---------|
| **Performance** | Rápido | Más rápido (basado en Starlette) | ✅ FastAPI |
| **Documentación Automática** | No | Sí (OpenAPI/Swagger) | ✅ FastAPI |
| **Validación de Datos** | Manual | Automática (Pydantic) | ✅ FastAPI |
| **Type Hints** | Opcional | Requerido (mejor DX) | ✅ FastAPI |
| **Ecosistema** | Bueno | Excelente | ✅ FastAPI |
| **Curva de Aprendizaje** | Media | Baja | ✅ FastAPI |
| **Async/Await** | Sí | Sí | ⚖️ Empate |
| **WebSockets** | Sí | Sí | ⚖️ Empate |
| **Comunidad** | Buena | Muy activa | ✅ FastAPI |

### Ventajas de FastAPI

✅ **Documentación Automática**:
- Swagger UI en `/docs`
- ReDoc en `/redoc`
- OpenAPI schema automático

✅ **Validación Automática**:
- Pydantic models para request/response
- Validación en tiempo de ejecución
- Errores claros y descriptivos

✅ **Mejor Developer Experience**:
- Type hints obligatorios
- Autocompletado en IDEs
- Menos código boilerplate

✅ **Performance**:
- Basado en Starlette (uno de los frameworks más rápidos)
- Comparable con NodeJS y Go

✅ **Dependency Injection**:
- Sistema de dependencias integrado
- Perfecto para autenticación, DB sessions, etc.

### Ejemplo de Código

**aiohttp (antes)**:
```python
from aiohttp import web

async def messages(request):
    body = await request.json()
    # ... procesamiento ...
    return web.Response(status=200)

app = web.Application()
app.router.add_post("/api/messages", messages)
```

**FastAPI (ahora)**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class MessageRequest(BaseModel):
    text: str
    user_id: str

@app.post("/api/messages")
async def messages(request: MessageRequest):
    # ... procesamiento ...
    return {"status": "success"}

# Swagger UI automático en /docs
```

---

## 🐘 PostgreSQL con pgvector vs Cosmos DB

### ¿Por qué PostgreSQL + pgvector?

| Aspecto | Cosmos DB | PostgreSQL + pgvector | Ganador |
|---------|-----------|----------------------|---------|
| **Costo** | Alto ($75+/mes) | Bajo (<$30/mes Azure) | ✅ PostgreSQL |
| **Búsqueda Vectorial** | No nativa | Sí (pgvector) | ✅ PostgreSQL |
| **SQL Familiar** | No | Sí (estándar SQL) | ✅ PostgreSQL |
| **Migraciones** | Propietario | Estándar (portable) | ✅ PostgreSQL |
| **Herramientas** | Limitadas | Muchas (pgAdmin, DBeaver) | ✅ PostgreSQL |
| **JSON Support** | Sí | Sí (JSONB) | ⚖️ Empate |
| **Escalabilidad Global** | Excelente | Buena | ✅ Cosmos DB |
| **Consistencia** | Eventual | Fuerte (ACID) | ✅ PostgreSQL |

### Ventajas de PostgreSQL con pgvector

✅ **Búsqueda Vectorial Nativa**:
- Almacenar embeddings de OpenAI directamente
- Búsqueda por similitud con operador `<->`
- Índices HNSW para performance
- **Reemplaza o complementa Azure Cognitive Search**

✅ **Costo Reducido**:
- Azure Database for PostgreSQL Flexible Server
- Tier básico: ~$25-30/mes
- vs Cosmos DB: ~$75+/mes

✅ **SQL Estándar**:
- Queries familiares
- ORMs conocidos (SQLAlchemy, Tortoise ORM)
- Migraciones con Alembic

✅ **JSONB para Flexibilidad**:
- Almacenar datos estructurados y semiestructurados
- Índices en campos JSON
- Queries eficientes

✅ **Full-Text Search**:
- PostgreSQL tiene FTS nativo
- tsvector y tsquery
- Puede reemplazar parte de Cognitive Search

✅ **Portable**:
- No lock-in con Azure
- Fácil migrar a AWS RDS, GCP CloudSQL, on-prem

### pgvector: Búsqueda Vectorial

**Instalación**:
```sql
CREATE EXTENSION vector;
```

**Crear Tabla con Embeddings**:
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  content TEXT,
  embedding vector(1536),  -- OpenAI ada-002 tiene 1536 dimensiones
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsqueda rápida
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

**Búsqueda por Similitud**:
```python
# Generar embedding de la query
query_embedding = openai.embeddings.create(
    model="text-embedding-ada-002",
    input="órdenes de compra pendientes"
).data[0].embedding

# Buscar documentos similares
results = await db.fetch("""
    SELECT content, metadata,
           1 - (embedding <=> $1) AS similarity
    FROM documents
    WHERE 1 - (embedding <=> $1) > 0.8
    ORDER BY embedding <=> $1
    LIMIT 5
""", query_embedding)
```

**Ventajas sobre Cognitive Search**:
- ✅ Mismo servidor que datos transaccionales
- ✅ Joins con otras tablas
- ✅ Transacciones ACID
- ✅ Menos latencia (sin llamada HTTP externa)
- ✅ Más barato

**Cuándo Usar Cognitive Search**:
- 🔍 Necesitas indexar documentos PDF/Word/etc
- 🔍 OCR de imágenes
- 🔍 Enrichment pipeline complejo
- 🔍 Faceted navigation avanzada

**Arquitectura Híbrida Recomendada**:
```
Knowledge Base Compleja → Azure Cognitive Search
Búsqueda de Conversaciones → PostgreSQL pgvector
Datos Transaccionales → PostgreSQL
```

---

## 🏗️ Arquitectura Actualizada

### Diagrama Simplificado de Datos

```
┌─────────────────────────────────────────┐
│     PostgreSQL con pgvector             │
├─────────────────────────────────────────┤
│                                         │
│  Tablas Transaccionales:                │
│  ├── conversations                      │
│  ├── messages                           │
│  ├── users                              │
│  ├── alerts                             │
│  └── audit_logs                         │
│                                         │
│  Tablas con Embeddings:                 │
│  ├── knowledge_base                     │
│  │   ├── content: TEXT                  │
│  │   ├── embedding: vector(1536)        │
│  │   └── metadata: JSONB                │
│  │                                      │
│  └── conversation_history               │
│      ├── message: TEXT                  │
│      ├── embedding: vector(1536)        │
│      └── context: JSONB                 │
│                                         │
│  Índices:                               │
│  ├── HNSW para búsqueda vectorial       │
│  ├── GIN para búsqueda JSONB            │
│  └── B-tree para queries estándar       │
└─────────────────────────────────────────┘
```

### Stack Tecnológico Actualizado

**Backend**:
```
FastAPI (Web Framework)
├── Pydantic (Validación)
├── SQLAlchemy (ORM)
├── Alembic (Migraciones)
├── asyncpg (Driver PostgreSQL async)
└── pgvector (Extensión PostgreSQL)
```

**Base de Datos**:
```
Azure Database for PostgreSQL Flexible Server
├── pgvector extension
├── JSONB support
├── Full-text search
└── Connection pooling (pgbouncer)
```

---

## 🔄 Plan de Migración

### Fase 0: Preparación (1 semana)

**Tareas**:
1. ✅ Provisionar Azure Database for PostgreSQL
2. ✅ Instalar extensión pgvector
3. ✅ Diseñar schema de base de datos
4. ✅ Configurar connection pooling
5. ✅ Setup Alembic para migraciones

**Scripts**:
```bash
# Provisionar PostgreSQL en Azure
az postgres flexible-server create \
  --name sgscm-postgres \
  --resource-group sgscm-rg \
  --location westus2 \
  --admin-user dbadmin \
  --admin-password <secure-password> \
  --sku-name Standard_B2s \
  --tier Burstable \
  --version 15 \
  --storage-size 32

# Habilitar pgvector
az postgres flexible-server parameter set \
  --name sgscm-postgres \
  --resource-group sgscm-rg \
  --name shared_preload_libraries \
  --value 'pgvector'
```

### Migración de aiohttp a FastAPI

**Paso 1: Instalar Dependencias**
```bash
pip install fastapi uvicorn[standard] sqlalchemy asyncpg alembic pgvector
pip uninstall aiohttp  # Opcional
```

**Paso 2: Crear Estructura FastAPI**
```
src/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app (antes app.py)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── messages.py  # Bot messages endpoint
│   │   ├── health.py    # Health checks
│   │   └── admin.py     # Admin endpoints
│   └── dependencies.py  # Dependency injection
├── database/
│   ├── __init__.py
│   ├── models.py        # SQLAlchemy models
│   ├── session.py       # Database session
│   └── crud.py          # CRUD operations
├── migrations/          # Alembic migrations
│   └── versions/
└── schemas/             # Pydantic schemas
    ├── __init__.py
    ├── conversation.py
    ├── message.py
    └── user.py
```

**Paso 3: Definir Modelos SQLAlchemy**
```python
# src/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from datetime import datetime

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    channel_id = Column(String(100))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String(50))  # 'user' or 'assistant'
    content = Column(Text)
    embedding = Column(Vector(1536))  # OpenAI embedding
    intent = Column(String(100))
    entities = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'

    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    content = Column(Text)
    embedding = Column(Vector(1536))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Paso 4: App FastAPI Principal**
```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import messages, health, admin
from src.database.session import engine
from src.database import models

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Azure MS Teams Bot",
    description="Bot inteligente con FastAPI y PostgreSQL",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.on_event("startup")
async def startup():
    # Inicializar servicios
    await cache_service.connect()
    logger.info("Bot started with FastAPI + PostgreSQL")

@app.on_event("shutdown")
async def shutdown():
    await cache_service.disconnect()
    logger.info("Bot shutdown")
```

### Migración de Datos

Si tienes datos en Cosmos DB (actualmente no):
```python
# Script de migración
import asyncio
from src.database.session import AsyncSession
from azure.cosmos import CosmosClient

async def migrate_cosmos_to_postgres():
    # 1. Conectar a Cosmos DB
    cosmos_client = CosmosClient(url, key)
    container = cosmos_client.get_database_client(db).get_container_client(container_name)

    # 2. Leer datos
    items = list(container.read_all_items())

    # 3. Insertar en PostgreSQL
    async with AsyncSession() as session:
        for item in items:
            conversation = Conversation(
                user_id=item['userId'],
                metadata=item['metadata']
            )
            session.add(conversation)
        await session.commit()
```

---

## 💰 Comparación de Costos

### Opción Original (Cosmos DB)

| Servicio | Costo Mensual |
|----------|---------------|
| Cosmos DB (Serverless 25GB) | $75 |
| **Total Almacenamiento** | **$75** |

### Opción Actualizada (PostgreSQL)

| Servicio | Costo Mensual |
|----------|---------------|
| Azure Database for PostgreSQL Flexible (B2s) | $25-30 |
| **Total Almacenamiento** | **$25-30** |

**Ahorro**: ~$45-50/mes (~60% de reducción)

**Nota**: Si necesitas más capacidad:
- B2s: 2 vCores, 4GB RAM, 32GB storage
- D2s v3: 2 vCores, 8GB RAM, 128GB storage (~$70/mes, aún más barato que Cosmos DB)

---

## 📊 Comparación: Cognitive Search vs pgvector

### Cuándo Usar Cognitive Search

✅ Documentos de Office (PDF, Word, Excel)
✅ OCR de imágenes
✅ Múltiples fuentes de datos
✅ Enrichment pipeline complejo
✅ Faceted navigation avanzada

### Cuándo Usar pgvector

✅ Búsqueda de conversaciones
✅ Búsqueda semántica simple
✅ RAG (Retrieval Augmented Generation)
✅ Recomendaciones
✅ Clustering de documentos
✅ Necesitas joins con datos transaccionales

### Arquitectura Híbrida Recomendada

```
┌──────────────────────────────────────────┐
│         Azure Cognitive Search           │
│  - Knowledge Base (docs, PDFs)           │
│  - Políticas y procedimientos            │
│  - Manuales de usuario                   │
└──────────────────────────────────────────┘
                   ↓
         [Búsquedas Complejas]
                   ↓
┌──────────────────────────────────────────┐
│       PostgreSQL con pgvector            │
│  - Historial de conversaciones           │
│  - FAQs                                  │
│  - Búsqueda semántica de mensajes        │
│  - Datos transaccionales                 │
└──────────────────────────────────────────┘
```

---

## ✅ Beneficios de la Nueva Arquitectura

### 1. **Performance Mejorado**
- FastAPI es más rápido que aiohttp
- PostgreSQL con índices optimizados
- Menos llamadas HTTP externas (pgvector local)

### 2. **Costo Reducido**
- ~$45-50/mes de ahorro en almacenamiento
- Menos servicios Azure = menos overhead

### 3. **Developer Experience**
- FastAPI: Documentación automática
- SQLAlchemy: ORM familiar y poderoso
- Pydantic: Validación type-safe

### 4. **Flexibilidad**
- JSONB para datos semiestructurados
- pgvector para búsqueda vectorial
- SQL estándar para queries complejos

### 5. **Portabilidad**
- PostgreSQL es estándar
- No lock-in con Azure
- Fácil migrar a otros clouds

### 6. **Ecosistema Rico**
- Herramientas maduras (pgAdmin, DBeaver)
- ORMs conocidos
- Mucha documentación

---

## 🎯 Próximos Pasos

1. ✅ Revisar este documento
2. ✅ Aprobar stack tecnológico (FastAPI + PostgreSQL)
3. ✅ Provisionar PostgreSQL en Azure
4. ✅ Migrar código de aiohttp a FastAPI
5. ✅ Implementar modelos SQLAlchemy
6. ✅ Setup Alembic migrations
7. ✅ Implementar búsqueda con pgvector
8. ✅ Testing completo
9. ✅ Actualizar documentación

---

**Documento creado:** Noviembre 2025
**Stack actualizado:** FastAPI + PostgreSQL + pgvector
**Ahorro estimado:** ~$45-50/mes + mejor DX
