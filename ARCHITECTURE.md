# Arquitectura del Sistema - PoC Enriquecimiento de Productos

## 🎯 Visión General

Sistema modular que enriquece productos con IA, automatiza alertas de stock y proporciona un panel de administración.

## 🏗️ Componentes

| Componente | Tecnología | Puerto | Función |
|---|---|---|---|
| **Frontend** | React + Vite | 5173/80 | Panel admin para gestionar productos |
| **Backend Principal** | FastAPI | 8000 | API principal - orquesta servicios |
| **Microservicio IA** | FastAPI | 8001 | Genera descripciones y categorías |
| **Microservicio Alertas** | FastAPI | 8002 | Gestiona alertas de stock |
| **Base de Datos** | PostgreSQL | 5432 | Almacena productos y alertas |

## 📊 Flujo Principal

```
1. Usuario entra al Frontend (React)
2. Crea producto: {nombre, palabras clave, stock}
3. Backend llama a Microservicio IA → Genera descripción
4. Backend llama a Microservicio IA → Genera categoría
5. Backend guarda en PostgreSQL
6. Usuario simula venta → Backend actualiza stock
7. Si stock < 10 → Backend notifica a Microservicio Alertas
8. Microservicio Alertas genera y guarda la alerta
```

## 🔌 APIs

**Backend Principal** (`POST /products`)
```json
{
  "name": "Laptop Dell",
  "keywords": ["laptop", "dell", "intel"],
  "stock": 50
}
```
Retorna: Producto con descripción + categoría generadas por IA

**Venta** (`POST /products/{id}/sell`)
```json
{ "new_stock": 49 }
```

**Alerta de Stock** (generada automáticamente cuando stock < 10)
```json
{
  "product_name": "Laptop Dell",
  "current_stock": 8,
  "alert_message": "⚠️ Stock bajo"
}
```

## 🛠️ Stack Tecnológico

- **Backend**: Python (FastAPI) - tipado, rápido, buena documentación
- **Frontend**: React (Vite) - moderno, HMR rápido
- **DB**: PostgreSQL - robusto, features avanzadas
- **LLM**: OpenAI SDK (integrado en backend)
- **Deploy**: Docker + Docker Compose

## ⚡ Características de Resiliencia

| Característica | Implementación |
|---|---|
| **Reintentos** | 3 intentos con espera exponencial (1s → 2s → 4s) |
| **Timeouts** | OpenAI SDK: 30s, BD: 5s |
| **Health Checks** | `/health` en cada servicio |
| **Error Handling** | Si IA falla, retorna error sin crashear |

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
1. Usuario → Frontend: Click "Simular Venta"
2. Frontend → Backend Principal: POST /products/{id}/sell
3. Backend Principal → PostgreSQL: UPDATE stock
4. Si stock < 10:
   - Backend → Microservicio Alertas: POST /alerts
5. Microservicio Alertas → PostgreSQL: Guarda alerta
6. Backend → Frontend: {updated_stock}
```

---

## 🛡️ Estrategia de Resiliencia y Manejo de Errores

### 1. Timeouts Configurados

| Servicio          | Timeout | Razón                              |
|-------------------|---------|------------------------------------|
| OpenAI API        | 30s     | Generación puede tardar            |
| PostgreSQL        | 5s      | Queries deben ser rápidas          |

### 2. Circuit Breaker Pattern

```python
# Si el OpenAI SDK falla 5 veces consecutivas:
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
async def call_openai_api():
    # Intento 1: inmediato
    # Intento 2: después de 1s
    # Intento 3: después de 2s
    pass
```

### 4. Degradación Graceful

- **Si OpenAI SDK falla**: Retornar error 503 pero no crashear el sistema
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
logger.error("openai_api_timeout", timeout=30)

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
| Tasa de éxito alertas de stock    | > 90%        |

---