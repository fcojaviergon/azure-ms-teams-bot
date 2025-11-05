# Guía de Uso del Bot

## Descripción General

Este bot de Microsoft Teams está diseñado para interactuar con SAP Ariba y proporcionar información sobre procesos de procurement.

---

## Capacidades del Bot

### 1. Consultar Purchase Orders (PO)
Pregunta por órdenes de compra específicas o busca por criterios.

**Ejemplos:**
- "Muéstrame el PO PO1234567"
- "¿Cuál es el estado del purchase order PO8901234?"
- "Lista los últimos 5 purchase orders"
- "Busca POs del proveedor Acme Corp"

### 2. Consultar Purchase Requisitions (PR)
Obtén información sobre requisiciones de compra.

**Ejemplos:**
- "Muéstrame la requisición PR7654321"
- "¿Cuál es el estado de mi PR?"
- "Lista las PRs pendientes de aprobación"
- "Busca requisiciones del último mes"

### 3. Consultar Proveedores
Obtén información sobre suppliers.

**Ejemplos:**
- "Información del proveedor Acme Corp"
- "Lista los proveedores activos"
- "¿Cuál es el rating del supplier SUP12345?"
- "Busca proveedores en España"

### 4. Búsqueda General
Realiza búsquedas amplias en el sistema.

**Ejemplos:**
- "Busca todo relacionado con proyecto Alpha"
- "¿Qué documentos tenemos para el departamento de IT?"
- "Muéstrame contratos que expiran este mes"

### 5. Obtener Estado de Documentos
Verifica el estado de cualquier documento.

**Ejemplos:**
- "¿Cuál es el estado del documento PO1234567?"
- "¿Dónde está mi requisición?"
- "Estado de la factura INV9876543"

---

## Formato de Respuestas

El bot puede responder en diferentes formatos:

### 1. Respuestas de Texto
Respuestas directas y conversacionales.

```
Usuario: ¿Qué es un Purchase Order?
Bot: Un Purchase Order (PO) es un documento comercial que un comprador
     envía a un proveedor para autorizar una compra...
```

### 2. Adaptive Cards (cuando esté implementado)
Tarjetas interactivas con información estructurada.

### 3. Listas y Tablas
Para múltiples resultados.

```
Usuario: Lista los últimos 3 POs
Bot:
📋 Purchase Orders Recientes:
1. PO1234567 - Acme Corp - $15,000 - Aprobado
2. PO1234568 - Beta Inc - $8,500 - Pendiente
3. PO1234569 - Gamma LLC - $22,000 - En tránsito
```

---

## Comandos Especiales

### Ayuda
```
/ayuda
/help
```
Muestra esta guía de uso.

### Estado del Sistema
```
/status
/health
```
Verifica el estado del bot y conexiones.

### Limpiar Contexto
```
/clear
/reset
```
Reinicia la conversación actual.

---

## Entidades Reconocidas

El bot puede identificar automáticamente:

### IDs de Documentos
- **Purchase Orders**: PO seguido de 7-10 dígitos (ej: PO1234567)
- **Purchase Requisitions**: PR seguido de 7-10 dígitos (ej: PR7654321)
- **Invoices**: INV seguido de dígitos (ej: INV9876543)
- **Contracts**: CT o CON seguido de dígitos

### Fechas
- "último mes"
- "esta semana"
- "2024-01-15"
- "enero 2024"

### Cantidades
- "$10,000"
- "15000 USD"
- "€5.000"

### Proveedores
- Nombres de compañías
- IDs de suppliers (SUP12345)

---

## Flujos de Trabajo Comunes

### Flujo 1: Revisar un Purchase Order

```
Usuario: Muéstrame el PO PO1234567

Bot: [Información del PO]
     📄 Purchase Order: PO1234567
     🏢 Proveedor: Acme Corporation
     💰 Total: $15,000.00 USD
     📅 Fecha: 2024-01-15
     ✅ Estado: Aprobado

     Líneas de pedido:
     1. Laptops Dell - 10 unidades - $1,500 c/u

     ¿Necesitas más detalles?

Usuario: ¿Cuándo llegará?

Bot: Según la información de Ariba, la fecha estimada de
     entrega es 2024-02-01. El envío está programado
     para salir el 2024-01-25.
```

### Flujo 2: Crear una Requisición (cuando esté implementado)

```
Usuario: Necesito crear una PR

Bot: Perfecto, te ayudaré a crear una Purchase Requisition.
     ¿Qué productos o servicios necesitas?

Usuario: 5 monitores Samsung

Bot: Entendido: 5 monitores Samsung
     ¿Cuál es el presupuesto estimado?

Usuario: $2000

Bot: ¿Para qué departamento es esta compra?

Usuario: IT

Bot: [Resumen de la PR creada]
```

### Flujo 3: Buscar Información

```
Usuario: Busca información sobre el proyecto Alpha

Bot: He encontrado 12 documentos relacionados con "proyecto Alpha":

     📋 Purchase Orders (3):
     - PO1234567: Equipamiento - $45,000
     - PO1234580: Software licenses - $12,000
     - PO1234599: Consultoría - $85,000

     📝 Purchase Requisitions (5):
     - PR7654321: Hardware adicional - Pendiente
     ...

     📑 Contratos (2):
     - CT9876543: Contrato marco - Activo
     ...

     ¿Quieres ver los detalles de algún documento?
```

---

## Preguntas Frecuentes

### ¿El bot puede aprobar documentos?
Actualmente no. El bot solo proporciona información y ayuda con consultas.

### ¿Qué tan actualizados son los datos?
Los datos se cachean por 1 hora para optimizar rendimiento. Para datos en tiempo real, el bot consulta directamente a Ariba.

### ¿Puedo usar el bot fuera de horario laboral?
Sí, el bot está disponible 24/7.

### ¿Qué hacer si el bot no responde?
1. Verifica tu conexión a internet
2. Intenta reformular tu pregunta
3. Usa /status para verificar el estado del sistema
4. Contacta al equipo de soporte si el problema persiste

### ¿El bot guarda mi historial de conversaciones?
Sí, para proporcionar contexto en la conversación. Los datos se manejan según las políticas de privacidad de la empresa.

### ¿Puedo usar el bot en conversaciones grupales?
Sí, menciona al bot con @NombreDelBot para interactuar en canales de equipo.

---

## Mejores Prácticas

### 1. Sé Específico
❌ "Dame información"
✅ "Muéstrame el PO PO1234567"

### 2. Usa IDs de Documentos
❌ "El purchase order que hice ayer"
✅ "El PO PO1234567"

### 3. Proporciona Contexto
❌ "¿Cuándo llega?"
✅ "¿Cuándo llega el PO PO1234567?"

### 4. Usa Lenguaje Natural
El bot entiende lenguaje conversacional, no necesitas comandos exactos.

✅ "¿Me puedes ayudar con información del proveedor Acme?"
✅ "Necesito ver el estado de mi PR"
✅ "Busca órdenes de compra del mes pasado"

---

## Limitaciones Actuales

- No puede crear o modificar documentos (próximamente)
- No puede aprobar requisiciones o POs
- No tiene acceso a datos financieros sensibles sin autorización
- Respuestas limitadas a la información disponible en Ariba

---

## Feedback y Soporte

Si encuentras problemas o tienes sugerencias:
1. Usa el comando `/feedback` en el bot
2. Contacta al equipo de desarrollo
3. Reporta bugs en el sistema de tickets interno

---

## Roadmap de Funcionalidades

### Próximamente
- ✨ Creación de Purchase Requisitions
- ✨ Notificaciones proactivas de cambios de estado
- ✨ Integraciones con Power BI para reportes
- ✨ Aprobaciones rápidas directamente en Teams
- ✨ Comandos de voz
- ✨ Soporte multiidioma

---

## Glosario

- **PO (Purchase Order)**: Orden de compra
- **PR (Purchase Requisition)**: Requisición de compra
- **Supplier**: Proveedor
- **Line Item**: Línea de pedido/ítem
- **Approval**: Aprobación
- **Requisitioner**: Solicitante
- **Cost Center**: Centro de costos
