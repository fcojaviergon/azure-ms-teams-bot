# Estrategia de Cálculos y Exposición de Datos

## 🎯 El Problema

**Pregunta crítica**: ¿Quién debe hacer los cálculos - el LLM o Python?

### ❌ Approach Incorrecto: Dejar que el LLM calcule

```python
# MAL - Enviar datos crudos al LLM para que sume
user: "¿Cuál es el total de POs aprobadas este mes?"

# Backend envía datos crudos al LLM
context = """
PO-001: $15,000 USD
PO-002: $8,500 USD
PO-003: $1,200 USD
"""

# LLM calcula (PELIGROSO)
llm_response = "El total es $24,700 USD"  # ¿Es correcto? No lo sabemos
```

**Problemas**:
- ❌ LLMs pueden equivocarse en aritmética
- ❌ No hay garantía de exactitud
- ❌ Difícil de auditar
- ❌ No confiable para finanzas/compliance

### ✅ Approach Correcto: Python hace cálculos, LLM presenta

```python
# BIEN - Python calcula, LLM solo presenta
user: "¿Cuál es el total de POs aprobadas este mes?"

# 1. LLM extrae intent y parámetros
intent = "sum_pos"
params = {"status": "approved", "month": "current"}

# 2. Python hace query y cálculo PRECISO
pos = ariba_service.get_purchase_orders(filters=params)
total = Decimal(sum(po.total_amount for po in pos))  # Decimal para precisión

# 3. Python envía resultado calculado al LLM
context = f"""
Encontradas {len(pos)} POs aprobadas.
Total calculado (verificado): ${total:,.2f} USD
"""

# 4. LLM solo presenta en lenguaje natural
llm_response = f"He encontrado {len(pos)} órdenes de compra aprobadas este mes, con un total de ${total:,.2f} USD."
```

**Ventajas**:
- ✅ Cálculos precisos con Decimal
- ✅ Auditables y verificables
- ✅ Confianza en resultados financieros
- ✅ LLM se enfoca en UX, no en aritmética

---

## 🏗️ Arquitectura: Tres Approaches

### Approach 1: MCP Server 🔌

**Model Context Protocol** - Protocolo de Anthropic para exponer herramientas al LLM

#### Arquitectura MCP

```
┌─────────────────────────────────────┐
│         Claude/GPT-4 (LLM)          │
│  - Entiende qué herramienta usar    │
│  - Llama MCP tools                  │
└─────────────────┬───────────────────┘
                  │ MCP Protocol
                  ↓
┌─────────────────────────────────────┐
│         MCP Server (Python)         │
│  - Expone tools como MCP endpoints  │
│  - Hace cálculos precisos           │
│  - Retorna resultados estructurados │
├─────────────────────────────────────┤
│  Tools expuestas:                   │
│  - get_purchase_orders              │
│  - sum_po_amounts                   │
│  - get_supplier_spending            │
│  - calculate_budget_remaining       │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│         SAP Ariba API               │
└─────────────────────────────────────┘
```

#### Ejemplo MCP Server

```python
# src/mcp/ariba_server.py
from mcp import MCPServer, Tool
from decimal import Decimal

server = MCPServer(name="ariba-tools")

@server.tool()
async def sum_purchase_orders(
    status: str = None,
    month: str = None,
    supplier_id: str = None
) -> dict:
    """
    Suma el monto total de órdenes de compra.

    Args:
        status: Estado de las POs (approved, pending, etc.)
        month: Mes a consultar (YYYY-MM)
        supplier_id: ID del proveedor

    Returns:
        dict con total, count, currency
    """
    # 1. Query a Ariba
    filters = {}
    if status:
        filters['status'] = status
    if month:
        filters['created_month'] = month
    if supplier_id:
        filters['supplier_id'] = supplier_id

    pos = await ariba_service.get_purchase_orders(filters=filters)

    # 2. Cálculo PRECISO en Python
    total = Decimal('0')
    for po in pos.records:
        total += Decimal(str(po['total_amount']))

    # 3. Retornar datos estructurados
    return {
        "total": float(total),
        "count": len(pos.records),
        "currency": "USD",
        "breakdown": [
            {
                "po_number": po['po_number'],
                "amount": float(po['total_amount']),
                "supplier": po['supplier']
            }
            for po in pos.records
        ]
    }

@server.tool()
async def calculate_supplier_spending(
    supplier_id: str,
    start_date: str,
    end_date: str
) -> dict:
    """Calcula gasto total con un proveedor en un período."""
    # Query + cálculo preciso
    ...
    return {
        "supplier_id": supplier_id,
        "total_spending": float(total),
        "transaction_count": count,
        "average_per_transaction": float(total / count)
    }

# Iniciar servidor MCP
if __name__ == "__main__":
    server.run()
```

#### Uso desde el LLM

```python
# El LLM automáticamente decide usar el tool
user: "¿Cuánto hemos gastado con el proveedor SUP-001 este mes?"

# LLM genera llamada MCP
mcp_call = {
    "tool": "calculate_supplier_spending",
    "arguments": {
        "supplier_id": "SUP-001",
        "start_date": "2025-11-01",
        "end_date": "2025-11-30"
    }
}

# MCP Server ejecuta y retorna
result = {
    "supplier_id": "SUP-001",
    "total_spending": 45750.50,
    "transaction_count": 12,
    "average_per_transaction": 3812.54
}

# LLM presenta resultado
"Has gastado $45,750.50 USD con el proveedor SUP-001 este mes, distribuidos en 12 transacciones con un promedio de $3,812.54 por transacción."
```

**Ventajas MCP**:
- ✅ Protocolo estándar (Anthropic)
- ✅ Separación clara de responsabilidades
- ✅ Reutilizable en otros contextos
- ✅ Buena para múltiples LLMs

**Desventajas MCP**:
- ❌ Más complejo de implementar
- ❌ Requiere servidor adicional
- ❌ Azure OpenAI no tiene soporte nativo MCP (solo Anthropic)

---

### Approach 2: Azure OpenAI Function Calling 🔧

**Function Calling** - Feature nativo de Azure OpenAI

#### Arquitectura Function Calling

```
┌─────────────────────────────────────┐
│       Azure OpenAI (GPT-4)          │
│  - Lee function definitions         │
│  - Decide qué función llamar        │
│  - Genera parámetros                │
└─────────────────┬───────────────────┘
                  │ Function Call JSON
                  ↓
┌─────────────────────────────────────┐
│       FastAPI Backend               │
│  - Recibe function call             │
│  - Ejecuta función Python           │
│  - Retorna resultado                │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│         SAP Ariba API               │
└─────────────────────────────────────┘
```

#### Definición de Functions

```python
# src/services/openai_functions.py
ARIBA_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "sum_purchase_orders",
            "description": "Calcula el monto total de órdenes de compra según filtros. Usa esta función cuando el usuario pregunte por totales, sumas o gastos en POs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["approved", "pending", "rejected", "all"],
                        "description": "Estado de las POs a incluir"
                    },
                    "month": {
                        "type": "string",
                        "pattern": "^\\d{4}-\\d{2}$",
                        "description": "Mes en formato YYYY-MM (ej: 2025-11)"
                    },
                    "supplier_id": {
                        "type": "string",
                        "description": "ID del proveedor para filtrar"
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoría de compra"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_budget_variance",
            "description": "Calcula la variación entre el presupuesto asignado y el gasto real en un período.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Departamento a analizar"
                    },
                    "month": {
                        "type": "string",
                        "description": "Mes en formato YYYY-MM"
                    },
                    "budget_amount": {
                        "type": "number",
                        "description": "Monto presupuestado"
                    }
                },
                "required": ["department", "month", "budget_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_suppliers_by_spending",
            "description": "Obtiene los proveedores con mayor gasto en un período, ordenados de mayor a menor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Fecha inicio YYYY-MM-DD"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Fecha fin YYYY-MM-DD"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Número de proveedores a retornar"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    }
]
```

#### Implementación de Functions

```python
# src/services/ariba_calculations.py
from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime

class AribaCalculations:
    """Cálculos precisos para datos de Ariba - NUNCA confiar en LLM para esto."""

    @staticmethod
    async def sum_purchase_orders(
        status: str = None,
        month: str = None,
        supplier_id: str = None,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Suma órdenes de compra con precisión decimal.

        Returns:
            Dict con total, count, breakdown, etc.
        """
        # 1. Query Ariba con filtros
        filters = {}
        if status and status != "all":
            filters['status'] = status
        if month:
            filters['created_month'] = month
        if supplier_id:
            filters['supplier_id'] = supplier_id
        if category:
            filters['category'] = category

        response = await ariba.get_purchase_orders(filters=filters)

        # 2. Cálculos PRECISOS con Decimal
        total_amount = Decimal('0')
        currency_totals = {}  # Agrupar por moneda
        supplier_totals = {}   # Agrupar por proveedor

        for po in response.records:
            amount = Decimal(str(po['total_amount']))
            currency = po.get('currency', 'USD')
            supplier = po.get('supplier')

            # Total general
            total_amount += amount

            # Total por moneda
            if currency not in currency_totals:
                currency_totals[currency] = Decimal('0')
            currency_totals[currency] += amount

            # Total por proveedor
            if supplier not in supplier_totals:
                supplier_totals[supplier] = Decimal('0')
            supplier_totals[supplier] += amount

        # 3. Retornar datos estructurados y VERIFICADOS
        return {
            "success": True,
            "total_amount": float(total_amount),
            "count": len(response.records),
            "currency_breakdown": {
                curr: float(amt) for curr, amt in currency_totals.items()
            },
            "supplier_breakdown": {
                supp: float(amt) for supp, amt in supplier_totals.items()
            },
            "filters_applied": filters,
            "calculated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    async def calculate_budget_variance(
        department: str,
        month: str,
        budget_amount: float
    ) -> Dict[str, Any]:
        """Calcula variación presupuestaria."""
        # 1. Obtener gasto real
        filters = {
            'department': department,
            'created_month': month
        }
        result = await AribaCalculations.sum_purchase_orders(**filters)
        actual_spending = Decimal(str(result['total_amount']))
        budget = Decimal(str(budget_amount))

        # 2. Calcular variación
        variance = budget - actual_spending
        variance_percentage = (variance / budget * 100) if budget > 0 else Decimal('0')

        return {
            "success": True,
            "department": department,
            "month": month,
            "budget_amount": float(budget),
            "actual_spending": float(actual_spending),
            "variance": float(variance),
            "variance_percentage": float(variance_percentage),
            "status": "under_budget" if variance > 0 else "over_budget",
            "po_count": result['count']
        }

    @staticmethod
    async def get_top_suppliers_by_spending(
        start_date: str,
        end_date: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Top proveedores por gasto."""
        # 1. Query todas las POs del período
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        response = await ariba.get_purchase_orders(filters=filters)

        # 2. Agrupar y sumar por proveedor
        supplier_spending = {}
        for po in response.records:
            supplier_id = po['supplier_id']
            supplier_name = po['supplier']
            amount = Decimal(str(po['total_amount']))

            if supplier_id not in supplier_spending:
                supplier_spending[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'total_spending': Decimal('0'),
                    'po_count': 0
                }

            supplier_spending[supplier_id]['total_spending'] += amount
            supplier_spending[supplier_id]['po_count'] += 1

        # 3. Ordenar por gasto (mayor a menor)
        sorted_suppliers = sorted(
            supplier_spending.values(),
            key=lambda x: x['total_spending'],
            reverse=True
        )[:limit]

        # 4. Convertir a float para JSON
        for supplier in sorted_suppliers:
            supplier['total_spending'] = float(supplier['total_spending'])

        return {
            "success": True,
            "period": f"{start_date} to {end_date}",
            "top_suppliers": sorted_suppliers,
            "total_suppliers": len(supplier_spending)
        }
```

#### Flujo Completo con Function Calling

```python
# src/services/openai_service.py
async def process_with_function_calling(user_message: str) -> str:
    """Procesa mensaje con function calling."""

    # 1. Primera llamada al LLM con functions disponibles
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente de procurement. Usa las funciones disponibles para cálculos precisos."},
            {"role": "user", "content": user_message}
        ],
        tools=ARIBA_FUNCTIONS,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # 2. Si el LLM quiere llamar una función
    if message.tool_calls:
        # 3. Ejecutar función(es) en Python
        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Ejecutar función Python (cálculo preciso)
            if function_name == "sum_purchase_orders":
                result = await AribaCalculations.sum_purchase_orders(**arguments)
            elif function_name == "calculate_budget_variance":
                result = await AribaCalculations.calculate_budget_variance(**arguments)
            elif function_name == "get_top_suppliers_by_spending":
                result = await AribaCalculations.get_top_suppliers_by_spending(**arguments)

            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result)
            })

        # 4. Segunda llamada al LLM con resultados de funciones
        final_response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Presenta los resultados de manera clara y profesional."},
                {"role": "user", "content": user_message},
                message,
                *tool_results
            ]
        )

        return final_response.choices[0].message.content

    # Si no necesita funciones, retornar respuesta directa
    return message.content
```

#### Ejemplo de Uso

```python
user: "¿Cuánto hemos gastado en total este mes en POs aprobadas?"

# 1. LLM decide llamar sum_purchase_orders
function_call = {
    "name": "sum_purchase_orders",
    "arguments": {
        "status": "approved",
        "month": "2025-11"
    }
}

# 2. Python ejecuta cálculo PRECISO
result = {
    "total_amount": 245750.50,
    "count": 47,
    "currency_breakdown": {
        "USD": 245750.50
    },
    "supplier_breakdown": {
        "Acme Corp": 150000.00,
        "Global Tech": 85750.50,
        "Office Pro": 10000.00
    }
}

# 3. LLM presenta resultado
response = """
Este mes has gastado **$245,750.50 USD** en 47 órdenes de compra aprobadas.

Desglose por proveedor:
• Acme Corp: $150,000.00 (61%)
• Global Tech: $85,750.50 (35%)
• Office Pro: $10,000.00 (4%)
"""
```

**Ventajas Function Calling**:
- ✅ Nativo en Azure OpenAI
- ✅ Bien documentado
- ✅ Fácil de implementar
- ✅ No requiere servidor adicional
- ✅ Cálculos precisos en Python

**Desventajas Function Calling**:
- ❌ Acoplado a OpenAI
- ❌ Menos flexible que MCP

---

### Approach 3: Hybrid (Recomendado) 🎯

**Mejor de ambos mundos**: Function Calling + Computation Layer

#### Arquitectura Híbrida

```
User Query
    ↓
┌─────────────────────────────────────┐
│   Intent Recognition (LLM)          │
│   - Identifica intent               │
│   - Extrae parámetros               │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Computation Layer (Python)        │
│   ┌───────────────────────────────┐ │
│   │  AribaCalculations            │ │
│   │  - sum_purchase_orders()      │ │
│   │  - calculate_variance()       │ │
│   │  - aggregate_by_supplier()    │ │
│   └───────────────────────────────┘ │
│                                     │
│   ┌───────────────────────────────┐ │
│   │  AnalyticsEngine              │ │
│   │  - compute_trends()           │ │
│   │  - forecast_spending()        │ │
│   │  - anomaly_detection()        │ │
│   └───────────────────────────────┘ │
└─────────────────┬───────────────────┘
                  ↓
         Structured Result
                  ↓
┌─────────────────────────────────────┐
│   Presentation Layer (LLM)          │
│   - Genera respuesta en NL          │
│   - Crea visualizaciones            │
│   - Sugiere acciones                │
└─────────────────────────────────────┘
```

#### Ventajas Approach Híbrido

1. **Separación de Responsabilidades**:
   - LLM: Comprensión y presentación
   - Python: Cálculos y lógica de negocio

2. **Auditabilidad**:
   - Cada cálculo es verificable
   - Logs de todas las operaciones
   - Trazabilidad completa

3. **Performance**:
   - Cálculos eficientes en Python
   - Cache de resultados complejos
   - PostgreSQL para agregaciones pesadas

4. **Flexibilidad**:
   - Fácil agregar nuevas funciones
   - Cambiar LLM sin afectar cálculos
   - Testing unitario de cálculos

---

## 🏆 Recomendación Final

### Stack Recomendado

```python
FastAPI
├── Azure OpenAI Function Calling
│   └── Intent Recognition
│
├── Computation Layer (Python)
│   ├── AribaCalculations (Decimal arithmetic)
│   ├── AnalyticsEngine (pandas, numpy)
│   └── CacheManager (Redis + PostgreSQL)
│
├── Data Layer
│   ├── PostgreSQL (aggregations, pgvector)
│   └── Redis (hot cache)
│
└── Presentation Layer
    ├── Azure OpenAI (natural language)
    ├── Adaptive Cards (Teams)
    └── Charts (QuickChart, Plotly)
```

### Flujo Recomendado

```python
# Ejemplo: "¿Cuánto gastamos en IT este mes vs presupuesto?"

# 1. Intent Recognition (LLM)
intent = await openai_service.extract_intent(user_message)
# → intent="budget_variance", params={"department": "IT", "month": "current"}

# 2. Computation (Python - PRECISO)
result = await AribaCalculations.calculate_budget_variance(
    department="IT",
    month="2025-11",
    budget_amount=500000.00
)
# → {budget: 500000, actual: 445750.50, variance: 54249.50, percentage: 10.85%}

# 3. Analytics (opcional)
trend = await AnalyticsEngine.compute_monthly_trend(
    department="IT",
    months=6
)
# → trend_direction="decreasing", forecast_next_month=420000

# 4. Presentation (LLM)
response = await openai_service.generate_response(
    template="budget_variance",
    data={**result, "trend": trend}
)
# → Rich natural language response with insights

# 5. Visualization (opcional)
if user_wants_chart:
    chart_url = await ChartGenerator.create_budget_chart(result)
    # → PNG chart URL
```

---

## 📊 Ejemplo Completo de Implementación

```python
# src/api/routes/analytics.py
from fastapi import APIRouter, Depends
from src.services.ariba_calculations import AribaCalculations
from src.services.openai_service import openai_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.post("/query")
async def process_analytics_query(query: str):
    """
    Endpoint principal para queries de analytics.
    Combina LLM para intent + Python para cálculos.
    """
    # 1. LLM extrae intent y parámetros
    analysis = await openai_service.analyze_query(
        query=query,
        available_functions=AribaCalculations.get_function_list()
    )

    # 2. Ejecutar cálculo en Python (NUNCA en LLM)
    if analysis.function_name == "sum_purchase_orders":
        result = await AribaCalculations.sum_purchase_orders(
            **analysis.parameters
        )
    elif analysis.function_name == "calculate_budget_variance":
        result = await AribaCalculations.calculate_budget_variance(
            **analysis.parameters
        )
    # ... más funciones

    # 3. Log para auditoría
    await audit_log.log_calculation(
        user_id=current_user.id,
        function=analysis.function_name,
        parameters=analysis.parameters,
        result=result
    )

    # 4. LLM genera respuesta natural
    response = await openai_service.generate_response(
        template=analysis.response_template,
        data=result,
        user_context=current_user.preferences
    )

    # 5. Opcional: generar visualización
    if analysis.needs_chart:
        chart = await ChartGenerator.create_chart(
            chart_type=analysis.chart_type,
            data=result
        )
        response["chart_url"] = chart.url

    return {
        "query": query,
        "intent": analysis.intent,
        "result": result,  # Datos estructurados
        "response": response,  # Lenguaje natural
        "calculated_at": datetime.utcnow()
    }
```

---

## 🔒 Principios de Seguridad en Cálculos

### 1. Siempre usar Decimal para dinero

```python
# ❌ MAL - float pierde precisión
total = 0.1 + 0.2  # → 0.30000000000000004

# ✅ BIEN - Decimal es preciso
from decimal import Decimal
total = Decimal('0.1') + Decimal('0.2')  # → Decimal('0.3')
```

### 2. Validar inputs

```python
def sum_purchase_orders(month: str, ...):
    # Validar formato
    if not re.match(r'^\d{4}-\d{2}$', month):
        raise ValueError("Month must be YYYY-MM format")

    # Validar rango razonable
    year = int(month[:4])
    if year < 2020 or year > 2030:
        raise ValueError("Year out of reasonable range")
```

### 3. Auditar todo

```python
# Log cada cálculo para compliance
await audit_log.create(
    user_id=user.id,
    action="sum_purchase_orders",
    parameters={"month": "2025-11", "status": "approved"},
    result={"total": 245750.50, "count": 47},
    ip_address=request.client.host,
    timestamp=datetime.utcnow()
)
```

### 4. Verificar monedas

```python
# No sumar monedas diferentes sin conversión
def sum_with_currency_check(amounts: List[Tuple[Decimal, str]]):
    currencies = set(curr for _, curr in amounts)
    if len(currencies) > 1:
        raise ValueError(f"Multiple currencies detected: {currencies}")

    total = sum(amt for amt, _ in amounts)
    currency = currencies.pop()
    return total, currency
```

---

## 🎯 Resumen: ¿Qué Approach Usar?

| Caso de Uso | Approach Recomendado |
|-------------|----------------------|
| **Cálculos financieros críticos** | ✅ Hybrid (Python calcula) |
| **Reportes complejos** | ✅ Hybrid + Analytics Engine |
| **Queries simples** | ✅ Function Calling directo |
| **Integración multi-LLM** | 🔌 MCP Server |
| **Prototipo rápido** | ✅ Function Calling |
| **Producción enterprise** | ✅ Hybrid + Auditoría |

### Decisión Final para Sierra Gorda SCM

**Recomendación: Hybrid Approach con Azure OpenAI Function Calling**

**Razones**:
1. ✅ Cálculos precisos en Python (compliance financiero)
2. ✅ Nativo en Azure OpenAI (no requiere infraestructura adicional)
3. ✅ Auditabilidad completa (cada cálculo loggeado)
4. ✅ Fácil testing unitario de cálculos
5. ✅ Performance óptimo (cache + PostgreSQL aggregations)

---

## 📁 Estructura de Archivos Propuesta

```
src/
├── services/
│   ├── openai_service.py           # Intent recognition
│   ├── openai_functions.py         # Function definitions
│   ├── ariba_calculations.py       # ⭐ Cálculos precisos (Decimal)
│   ├── analytics_engine.py         # Analytics avanzado
│   └── chart_generator.py          # Visualizaciones
│
├── api/
│   └── routes/
│       ├── analytics.py            # Endpoint principal analytics
│       └── calculations.py         # Endpoints de cálculos directos
│
└── database/
    └── models.py
        ├── AuditLog                 # Para compliance
        └── CalculationCache         # Cache de resultados
```

---

**Documento creado:** Noviembre 2025
**Approach recomendado:** Hybrid - Azure OpenAI Function Calling + Python Computation Layer
**Principio clave:** ⚠️ NUNCA confiar cálculos financieros al LLM
