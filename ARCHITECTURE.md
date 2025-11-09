# Arquitectura del Sistema - E-Commerce Product Enrichment PoC

## 📐 Decisiones Arquitectónicas (ADRs)

### ADR-001: Arquitectura de Microservicios

**Contexto**: Necesitamos un sistema escalable que separe responsabilidades entre enriquecimiento de productos, gestión de datos y automatización.

**Decisión**: Implementar una arquitectura de microservicios con 3 servicios principales:
1. **Backend Principal (BFF)** - Orquestador y gestor de estado
2. **Microservicio IA** - Especializado en generación de contenido
3. **Motor de Automatización (n8n)** - Gestión de workflows

**Consecuencias**:
- ✅ **Pros**: 
  - Separación de responsabilidades (SRP)
  - Escalabilidad independiente de cada servicio
  - Facilita testing y deployment aislado
  - El servicio IA puede ser reutilizado por otros sistemas
- ❌ **Contras**:
  - Mayor complejidad operacional
  - Latencia adicional por comunicación inter-servicios
  - Requiere manejo de fallos distribuidos

**Trade-offs Aceptados**: Sacrificamos simplicidad por escalabilidad y mantenibilidad a largo plazo.

---

### ADR-002: FastAPI como Framework Backend

**Contexto**: Necesitamos un framework Python moderno, rápido y con buen soporte para APIs REST.

**Decisión**: Usar FastAPI para ambos backends (Principal y Microservicio IA).

**Alternativas Consideradas**:
- **Flask**: Más maduro pero menos performante y sin tipado nativo
- **Django REST Framework**: Demasiado pesado para microservicios
- **Express.js (Node)**: Requeriría cambio de lenguaje

**Razones**:
- ✅ Tipado automático con Pydantic (validación y documentación)
- ✅ Alto rendimiento (basado en Starlette y Uvicorn)
- ✅ Documentación OpenAPI automática
- ✅ Async/await nativo para llamadas HTTP concurrentes
- ✅ Ecosistema Python ideal para integración con LLMs

---

### ADR-003: PostgreSQL como Base de Datos

**Contexto**: Necesitamos persistencia relacional con soporte para tipos de datos complejos.

**Decisión**: PostgreSQL como base de datos principal.

**Alternativas Consideradas**:
- **MySQL**: Menos features avanzados (JSONB, arrays)
- **MongoDB**: Overkill para este modelo de datos estructurado
- **SQLite**: No apto para producción/concurrencia

**Razones**:
- ✅ Soporte nativo para JSONB (almacenar keywords como array)
- ✅ ACID compliance para consistencia de stock
- ✅ Excelente soporte en SQLAlchemy
- ✅ Gratuito y open-source
- ✅ Robusto para producción

---

### ADR-004: Comunicación Síncrona HTTP REST

**Contexto**: Los servicios necesitan comunicarse entre sí.

**Decisión**: Comunicación REST HTTP síncrona con timeouts y reintentos.

**Alternativas Consideradas**:
- **gRPC**: Más performante pero mayor complejidad
- **Message Queue (RabbitMQ/Kafka)**: Asíncrono, innecesario para PoC
- **GraphQL**: Overkill para comunicación interna

**Razones**:
- ✅ Simplicidad de implementación
- ✅ Debugging más sencillo
- ✅ Compatible con herramientas estándar (curl, Postman)
- ✅ Suficiente para un PoC

**Estrategia de Resiliencia**:
```python
# Timeouts configurados
TIMEOUT_IA_SERVICE = 30s  # LLMs pueden tardar
TIMEOUT_WEBHOOK = 10s
TIMEOUT_DB = 5s

# Reintentos con exponential backoff
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # 1s, 2s, 4s
```

---

### ADR-005: n8n para Automatización

**Contexto**: Necesitamos un motor de workflows para alertas de stock.

**Decisión**: Usar n8n (low-code workflow automation).

**Alternativas Consideradas**:
- **Script LangChain**: Más código custom pero menos visual
- **Apache Airflow**: Demasiado pesado para workflows simples
- **Zapier/Make**: SaaS, no self-hosted

**Razones**:
- ✅ Visual y fácil de demostrar
- ✅ Self-hosted (cumple requisito Docker)
- ✅ Webhook trigger nativo
- ✅ Integración HTTP simple
- ✅ Exportable como JSON (versionable)

---

### ADR-006: React + Vite para Frontend

**Contexión**: UI moderna y reactiva para el panel admin.

**Decisión**: React con Vite como bundler.

**Alternativas Consideradas**:
- **Next.js**: SSR innecesario para admin panel interno
- **Vue.js**: Menos demanda en el mercado
- **Create React App**: Deprecado y más lento que Vite

**Razones**:
- ✅ Vite extremadamente rápido (HMR instantáneo)
- ✅ React es el estándar de la industria
- ✅ Ecosistema maduro de librerías
- ✅ Setup minimalista

---

## 🏗️ Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO FINAL                            │
│                    (Gerente de Bodega)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                     │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │  Formulario      │  │  Lista de Productos                │  │
│  │  Añadir Producto │  │  + Botón "Simular Venta"          │  │
│  └──────────────────┘  └────────────────────────────────────┘  │
│                     Puerto: 5173 (dev) / 80 (prod)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND PRINCIPAL (FastAPI - BFF)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Endpoints:                                               │   │
│  │ • POST /products   → Orquesta creación + IA             │   │
│  │ • GET  /products   → Lista productos de DB              │   │
│  │ • POST /products/{id}/sell → Venta + Alerta stock      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     Puerto: 8000                                 │
└──────────┬─────────────────────┬────────────────────┬───────────┘
           │                     │                    │
           │ HTTP                │ HTTP               │ Webhook
           ▼                     ▼                    ▼
┌──────────────────────┐  ┌─────────────────┐  ┌───────────────┐
│  MICROSERVICIO IA    │  │   PostgreSQL    │  │     n8n       │
│    (FastAPI)         │  │                 │  │ Automatización│
│ ┌──────────────────┐ │  │ ┌─────────────┐ │  │ ┌───────────┐ │
│ │/generate/        │ │  │ │   Tabla:    │ │  │ │ Workflow: │ │
│ │ description      │ │  │ │  products   │ │  │ │  Stock    │ │
│ │                  │ │  │ │             │ │  │ │  Alert    │ │
│ │/generate/        │ │  │ │ • id        │ │  │ └───────────┘ │
│ │ category         │ │  │ │ • name      │ │  │               │
│ └──────────────────┘ │  │ │ • keywords  │ │  │ • Webhook     │
│         │            │  │ │ • stock     │ │  │ • HTTP Mock   │
│         │ API        │  │ │ • desc      │ │  │ • Formatear   │
│         ▼            │  │ │ • category  │ │  │ • Log/Email   │
│  ┌──────────────┐   │  │ └─────────────┘ │  │               │
│  │ OpenAI API   │   │  │   Puerto: 5432  │  │ Puerto: 5678  │
│  │ o Gemini     │   │  └─────────────────┘  └───────────────┘
│  └──────────────┘   │
│   Puerto: 8001      │
└─────────────────────┘

                    ┌─────────────────────┐
                    │   Docker Network    │
                    │   app-network       │
                    └─────────────────────┘
```

---

## 🔄 Flujos de Datos Principales

### Flujo 1: Crear Producto con IA

```
1. Usuario → Frontend: Ingresa {name, keywords, stock}
2. Frontend → Backend Principal: POST /products
3. Backend Principal → Microservicio IA: POST /generate/description
4. Microservicio IA → OpenAI API: Prompt con name + keywords
5. OpenAI API → Microservicio IA: Descripción generada
6. Microservicio IA → Backend Principal: {generated_description}
7. Backend Principal → Microservicio IA: POST /generate/category
8. Microservicio IA → OpenAI API: Prompt con name + description
9. OpenAI API → Microservicio IA: Categoría sugerida
10. Microservicio IA → Backend Principal: {suggested_category}
11. Backend Principal → PostgreSQL: INSERT producto completo
12. PostgreSQL → Backend Principal: Producto guardado
13. Backend Principal → Frontend: Producto completo con IA
14. Frontend: Actualiza lista automáticamente
```

**Tiempo estimado**: 5-10 segundos (por las llamadas a LLM)

---

### Flujo 2: Simular Venta y Alerta de Stock

```
1. Usuario → Frontend: Click "Simular Venta" en producto
2. Frontend → Backend Principal: POST /products/{id}/sell
3. Backend Principal → PostgreSQL: UPDATE stock = stock - 1
4. Backend Principal: Verifica si stock < 10
5. SI stock < 10:
   a. Backend Principal → n8n Webhook: 
      {product_name, current_stock, product_id}
   b. n8n → API Mock (dummyjson): GET precio proveedor
   c. n8n: Formatea mensaje de alerta
   d. n8n: Log en consola / Envía email
6. Backend Principal → Frontend: {updated_stock}
7. Frontend: Actualiza UI con nuevo stock
```

---

## 🛡️ Estrategia de Resiliencia y Manejo de Errores

### 1. Timeouts Configurados

| Servicio          | Timeout | Razón                              |
|-------------------|---------|------------------------------------|
| LLM API           | 30s     | Generación puede tardar            |
| Microservicio IA  | 35s     | Incluye timeout del LLM + buffer   |
| PostgreSQL        | 5s      | Queries deben ser rápidas          |
| n8n Webhook       | 10s     | No bloqueante, puede fallar        |

### 2. Circuit Breaker Pattern

```python
# Si el Microservicio IA falla 5 veces consecutivas:
# → Abrimos el circuito por 60 segundos
# → Retornamos error inmediato sin llamar
# → Después de 60s, intentamos 1 request (half-open)
```

### 3. Reintentos con Exponential Backoff

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(requests.exceptions.Timeout)
)
async def call_ia_service():
    # Intento 1: inmediato
    # Intento 2: después de 1s
    # Intento 3: después de 2s
    pass
```

### 4. Degradación Graceful

- **Si Microservicio IA falla**: Retornar error 503 pero no crashear el sistema
- **Si n8n webhook falla**: Logear error pero completar la venta (no es crítico)
- **Si PostgreSQL falla**: Retornar error 500 y logear para investigación

### 5. Health Checks

Todos los servicios exponen `/health`:

```json
GET /health
{
  "status": "healthy",
  "service": "backend-principal",
  "timestamp": "2025-11-08T10:30:00Z",
  "dependencies": {
    "database": "ok",
    "ia_service": "ok"
  }
}
```

---

## 📊 Estrategia de Logging y Observabilidad

### Niveles de Log

```python
import structlog

logger = structlog.get_logger()

# INFO: Operaciones normales
logger.info("product_created", product_id=123, name="Producto X")

# WARNING: Situaciones anómalas pero no críticas
logger.warning("stock_low", product_id=123, stock=8)

# ERROR: Errores que requieren atención
logger.error("ia_service_timeout", service="description", timeout=30)

# CRITICAL: Fallos del sistema
logger.critical("database_connection_lost")
```

### Logs Estructurados (JSON)

```json
{
  "timestamp": "2025-11-08T10:30:00Z",
  "level": "info",
  "service": "backend-principal",
  "event": "product_created",
  "product_id": 123,
  "ia_generation_time": 7.2,
  "trace_id": "abc-def-ghi"
}
```

### Puntos Críticos de Logging

1. **Inicio/fin de requests** (latencia)
2. **Llamadas entre servicios** (troubleshooting)
3. **Errores de LLM** (monitoreo de costos)
4. **Alertas de stock** (auditoría)
5. **Fallos de DB** (disponibilidad)

---

## 🔐 Consideraciones de Seguridad (Futuro)

Para un PoC no se implementan, pero en producción:

- [ ] Autenticación JWT para usuarios
- [ ] Rate limiting en endpoints públicos
- [ ] Validación de input más estricta (SQL injection)
- [ ] HTTPS/TLS en todas las comunicaciones
- [ ] Secrets management (Vault, AWS Secrets)
- [ ] CORS configurado correctamente

---

## 📈 Escalabilidad Futura

### Horizontal Scaling

```yaml
# Múltiples instancias del mismo servicio
backend-principal:
  replicas: 3
  load_balancer: nginx

microservicio-ia:
  replicas: 5  # El más demandado
  load_balancer: nginx
```

### Caching

```python
# Redis para cachear descripciones ya generadas
@cache(ttl=3600)  # 1 hora
def get_product_description(name, keywords):
    # Si ya se generó, retornar del cache
    # Ahorra llamadas a LLM y $$$
    pass
```

### Message Queue (Async)

```
Frontend → Backend → RabbitMQ → Worker → LLM
                         ↓
                   Status: "processing"
                   Webhook cuando complete
```

---

## 🎯 Métricas de Éxito

| Métrica                           | Objetivo PoC |
|-----------------------------------|--------------|
| Tiempo creación producto          | < 15s        |
| Disponibilidad sistema            | > 95%        |
| Precisión categorización IA       | > 80%        |
| Tiempo respuesta GET /products    | < 500ms      |
| Tasa de éxito alertas n8n         | > 90%        |

---

## 📝 Limitaciones Conocidas del PoC

1. **No hay autenticación**: Cualquiera puede acceder
2. **Single tenant**: No multi-empresa
3. **Sin paginación eficiente**: GET /products retorna todo
4. **LLM calls no optimizados**: Sin cache ni batch processing
5. **n8n webhook es fire-and-forget**: No confirmación de entrega
6. **Sin backup automatizado de PostgreSQL**

---

## 🚀 Roadmap Post-PoC

### Fase 2: MVP
- Autenticación de usuarios
- Paginación y filtros
- Cache de llamadas LLM (Redis)
- Monitoring dashboard (Grafana)

### Fase 3: Producción
- Multi-tenancy
- Message queue para async processing
- CDN para frontend
- Backup y disaster recovery
- CI/CD pipeline

---

**Última actualización**: 2025-11-08  
**Versión**: 1.0.0  
**Autor**: Equipo Orquestia PoC
