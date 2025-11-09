# 📊 Diagramas de Arquitectura

## 🏗️ Sistema Completo

```mermaid
graph TB
    UI["🖥️ Frontend React<br/>Puerto: 5173"]
    BFF["⚙️ Backend FastAPI<br/>Puerto: 8000"]
    DB[("🗄️ PostgreSQL<br/>Puerto: 5432")]
    LLM["🧠 OpenAI API"]

    UI -->|HTTP| BFF
    BFF -->|SQL| DB
    BFF -->|HTTP| LLM

    style UI fill:#61dafb
    style BFF fill:#009688
    style DB fill:#336791
    style LLM fill:#10a37f
```

## 🔄 Crear Producto

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Frontend
    participant API as Backend
    participant LLM as OpenAI
    participant DB as PostgreSQL

    U->>UI: Ingresa producto
    UI->>API: POST /products
    API->>LLM: Genera descripción
    LLM-->>API: Descripción
    API->>LLM: Genera categoría
    LLM-->>API: Categoría
    API->>DB: Guarda producto
    DB-->>API: ✅
    API-->>UI: Producto enriquecido
    UI-->>U: Mostrar en lista
```

## � Venta y Alerta de Stock

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Frontend
    participant API as Backend
    participant LLM as OpenAI
    participant DB as PostgreSQL

    U->>UI: Click "Simular Venta"
    UI->>API: POST /products/{id}/sell
    API->>DB: UPDATE stock -= 1
    DB-->>API: ✅
    
    alt Stock < 10
        API->>LLM: Genera alerta
        LLM-->>API: Alerta formateada
        API->>API: Log en consola
    end
    
    API-->>UI: Nuevo stock
    UI-->>U: ✅ Venta completada
```

## 🐳 Docker Compose

```
docker-compose.yml
├── frontend (React)           :5173 / :80
├── backend-principal (FastAPI) :8000
├── microservicio-ia (FastAPI)  :8001
└── postgres                    :5432
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
