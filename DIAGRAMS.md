# 📊 Diagramas de Arquitectura

## 🏗️ Sistema Completo

```mermaid
graph TB
    UI["🖥️ Frontend React<br/>Puerto: 5173"]
    BFF["⚙️ Backend Principal<br/>Puerto: 8000"]
    IA["🧠 Microservicio IA<br/>Puerto: 8001"]
    ALERTS["🚨 Microservicio Alertas<br/>Puerto: 8002"]
    DB[("🗄️ PostgreSQL<br/>Puerto: 5432")]
    LLM["� OpenAI API"]

    UI -->|HTTP| BFF
    BFF -->|HTTP| IA
    BFF -->|HTTP| ALERTS
    BFF -->|SQL| DB
    ALERTS -->|SQL| DB
    IA -->|HTTP| LLM

    style UI fill:#61dafb
    style BFF fill:#009688
    style IA fill:#673ab7
    style ALERTS fill:#f44336
    style DB fill:#336791
    style LLM fill:#10a37f
```

## 🔄 Crear Producto

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Frontend
    participant API as Backend
    participant IA as Microservicio IA
    participant LLM as OpenAI
    participant DB as PostgreSQL

    U->>UI: Ingresa producto
    UI->>API: POST /products
    API->>IA: POST /generate/description
    IA->>LLM: Prompt
    LLM-->>IA: Descripción
    IA-->>API: Descripción
    API->>IA: POST /generate/category
    IA->>LLM: Prompt
    LLM-->>IA: Categoría
    IA-->>API: Categoría
    API->>DB: INSERT producto
    DB-->>API: ✅
    API-->>UI: Producto completo
    UI-->>U: Mostrar en lista
```

## 🚨 Venta y Alerta de Stock

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Frontend
    participant API as Backend
    participant ALERTS as Microservicio Alertas
    participant DB as PostgreSQL

    U->>UI: Click "Simular Venta"
    UI->>API: POST /products/{id}/sell
    API->>DB: UPDATE stock
    DB-->>API: ✅
    
    alt Stock < 10
        API->>ALERTS: POST /alerts
        ALERTS->>DB: INSERT alerta
        DB-->>ALERTS: ✅
        ALERTS-->>API: ✅
    end
    
    API-->>UI: Nuevo stock
    UI-->>U: ✅ Venta completada
```

## 🐳 Docker Compose

```
docker-compose.yml
├── frontend (React)              :5173 / :80
├── backend-principal (FastAPI)   :8000
├── microservicio-ia (FastAPI)    :8001
├── microservicio-alertas (FastAPI) :8002
└── postgres                      :5432
```

## � Base de Datos

```
Tabla: products
├── id (UUID)
├── name (string)
├── keywords (array)
├── stock (int)
├── description (text - generado por IA)
├── category (string - generado por IA)
├── created_at
└── updated_at
```

## �️ Manejo de Errores

| Error | Acción |
|-------|--------|
| Validación Pydantic ❌ | 400 Bad Request |
| OpenAI timeout ⏱️ | Retry (3x exponencial) → 503 |
| DB error 🗄️ | 500 Internal Server Error |
| Alerta fallida ⚠️ | Log warning (no falla request) |

## � Timeouts Configurados

| Servicio | Timeout | Razón |
|----------|---------|-------|
| OpenAI API | 30s | LLM puede tardar |
| PostgreSQL | 5s | Queries rápidas |
| Reintentos | 3x con backoff | 1s → 2s → 4s |

---

**Última actualización**: 2025-11-08  
**Versión**: 1.0.0
