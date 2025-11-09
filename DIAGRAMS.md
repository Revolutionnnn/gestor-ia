# Diagramas de Arquitectura

## 📐 Diagrama de Arquitectura del Sistema

```mermaid
graph TB
    subgraph "CAPA DE PRESENTACIÓN"
        UI[🖥️ Frontend React + Vite<br/>Puerto: 5173]
    end

    subgraph "CAPA DE APLICACIÓN"
        BFF[⚙️ Backend Principal FastAPI<br/>Puerto: 8000<br/><br/>Endpoints:<br/>• POST /products<br/>• GET /products<br/>• POST /products/:id/sell]
    end

    subgraph "CAPA DE SERVICIOS"
        IA[🤖 Microservicio IA FastAPI<br/>Puerto: 8001<br/><br/>Endpoints:<br/>• POST /generate/description<br/>• POST /generate/category]
        N8N[🔄 n8n Automation<br/>Puerto: 5678<br/><br/>Workflows:<br/>• Stock Alert]
    end

    subgraph "CAPA DE DATOS"
        DB[(🗄️ PostgreSQL<br/>Puerto: 5432<br/><br/>Tables:<br/>• products)]
    end

    subgraph "SERVICIOS EXTERNOS"
        LLM[🧠 OpenAI API / Gemini<br/><br/>Models:<br/>• GPT-4 Turbo<br/>• Gemini Pro]
        MOCK[📊 DummyJSON API<br/><br/>Mock:<br/>• Precios proveedores]
    end

    UI -->|HTTP REST| BFF
    BFF -->|HTTP REST| IA
    BFF -->|SQL| DB
    BFF -->|Webhook| N8N
    IA -->|API| LLM
    N8N -->|HTTP| MOCK

    style UI fill:#61dafb,stroke:#000,stroke-width:2px,color:#000
    style BFF fill:#009688,stroke:#000,stroke-width:2px,color:#fff
    style IA fill:#ff9800,stroke:#000,stroke-width:2px,color:#000
    style N8N fill:#ea4b71,stroke:#000,stroke-width:2px,color:#fff
    style DB fill:#336791,stroke:#000,stroke-width:2px,color:#fff
    style LLM fill:#10a37f,stroke:#000,stroke-width:2px,color:#fff
    style MOCK fill:#ffd43b,stroke:#000,stroke-width:2px,color:#000
```

## 🔄 Diagrama de Flujo: Crear Producto

```mermaid
sequenceDiagram
    actor User as 👤 Usuario
    participant UI as 🖥️ Frontend
    participant BFF as ⚙️ Backend Principal
    participant IA as 🤖 Microservicio IA
    participant LLM as 🧠 OpenAI/Gemini
    participant DB as 🗄️ PostgreSQL

    User->>UI: Ingresa formulario<br/>(name, keywords, stock)
    UI->>UI: Validación cliente
    
    UI->>BFF: POST /products<br/>{name, keywords, stock}
    
    Note over BFF: Orquestación de IA
    
    BFF->>IA: POST /generate/description<br/>{name, keywords}
    IA->>LLM: Prompt: "Genera descripción..."
    LLM-->>IA: Descripción generada
    IA-->>BFF: {generated_description}
    
    BFF->>IA: POST /generate/category<br/>{name, description}
    IA->>LLM: Prompt: "Clasifica producto..."
    LLM-->>IA: Categoría sugerida
    IA-->>BFF: {suggested_category}
    
    Note over BFF: Persistencia
    
    BFF->>DB: INSERT INTO products<br/>(name, keywords, stock,<br/>description, category)
    DB-->>BFF: Producto guardado (id: UUID)
    
    BFF-->>UI: 201 Created<br/>{producto completo}
    UI->>UI: Actualiza lista
    UI-->>User: ✅ Producto creado
    
    Note over User,DB: ⏱️ Tiempo total: ~5-10 segundos
```

## 💰 Diagrama de Flujo: Simular Venta y Alerta

```mermaid
sequenceDiagram
    actor User as 👤 Usuario
    participant UI as 🖥️ Frontend
    participant BFF as ⚙️ Backend Principal
    participant DB as 🗄️ PostgreSQL
    participant N8N as 🔄 n8n
    participant Mock as 📊 DummyJSON

    User->>UI: Click "Simular Venta"
    UI->>BFF: POST /products/{id}/sell
    
    BFF->>DB: BEGIN TRANSACTION
    BFF->>DB: SELECT stock<br/>WHERE id = {id}<br/>FOR UPDATE
    DB-->>BFF: current_stock = 10
    
    BFF->>BFF: new_stock = 10 - 1 = 9
    
    BFF->>DB: UPDATE products<br/>SET stock = 9<br/>WHERE id = {id}
    BFF->>DB: COMMIT
    
    alt Stock Bajo (< 10)
        Note over BFF: 🚨 Stock bajo detectado
        
        BFF->>N8N: POST webhook<br/>{product_id, product_name,<br/>current_stock: 9}
        
        Note over N8N: Workflow automático
        
        N8N->>Mock: GET /products/1<br/>(simula consulta proveedor)
        Mock-->>N8N: {price: $99.99}
        
        N8N->>N8N: Formatea mensaje:<br/>"ALERTA: Quedan 9 unidades<br/>de {name}. Precio: $99.99"
        
        N8N->>N8N: Log en consola /<br/>Envía email
        
        N8N-->>BFF: 200 OK
    end
    
    BFF-->>UI: 200 OK<br/>{stock: 9,<br/>low_stock_alert_sent: true}
    UI->>UI: Actualiza stock en tabla
    UI-->>User: ✅ Venta procesada<br/>⚠️ Stock bajo
```

## 🏗️ Diagrama de Contenedores Docker

```mermaid
graph LR
    subgraph "Docker Compose Network: app-network"
        subgraph "frontend"
            F[React App<br/>Nginx Server<br/>:80]
        end
        
        subgraph "backend-principal"
            B[FastAPI + Uvicorn<br/>:8000]
        end
        
        subgraph "microservicio-ia"
            I[FastAPI + Uvicorn<br/>:8001]
        end
        
        subgraph "n8n"
            N[n8n Workflow<br/>:5678]
        end
        
        subgraph "postgres"
            D[(PostgreSQL 16<br/>:5432)]
        end
        
        V1[Volume:<br/>postgres_data]
        V2[Volume:<br/>n8n_data]
    end

    F -->|proxy_pass| B
    B --> I
    B --> D
    B --> N
    D --> V1
    N --> V2

    style F fill:#61dafb,stroke:#333,stroke-width:2px
    style B fill:#009688,stroke:#333,stroke-width:2px
    style I fill:#ff9800,stroke:#333,stroke-width:2px
    style N fill:#ea4b71,stroke:#333,stroke-width:2px
    style D fill:#336791,stroke:#333,stroke-width:2px
    style V1 fill:#ffd700,stroke:#333,stroke-width:2px
    style V2 fill:#ffd700,stroke:#333,stroke-width:2px
```

## 🗄️ Diagrama de Modelo de Datos

```mermaid
erDiagram
    PRODUCTS {
        uuid id PK "Primary Key (UUID v4)"
        varchar name "Nombre del producto (max 200)"
        jsonb keywords "Array de palabras clave"
        integer stock "Stock actual (>= 0)"
        text description "Descripción generada por IA"
        varchar category "Categoría IA (formato: A > B > C)"
        timestamp created_at "Fecha de creación"
        timestamp updated_at "Última actualización"
    }

    PRODUCTS ||--o{ STOCK_ALERTS : "triggers"
    
    STOCK_ALERTS {
        uuid id PK "Primary Key"
        uuid product_id FK "Referencia a producto"
        integer stock_level "Stock cuando se disparó"
        timestamp triggered_at "Momento de la alerta"
        boolean webhook_sent "Si se envió a n8n"
    }

    note "Índices:
    - idx_products_stock (para queries de stock bajo)
    - idx_products_category (para filtros futuros)
    - idx_products_created_at (para ordenamiento)"
```

## 🔐 Diagrama de Manejo de Errores

```mermaid
graph TD
    A[Request llega a Backend Principal] --> B{Validación Pydantic}
    B -->|❌ Inválido| C[400 Bad Request]
    B -->|✅ Válido| D[Llama Microservicio IA]
    
    D --> E{IA Service<br/>disponible?}
    E -->|❌ Timeout| F[⏱️ Retry con<br/>Exponential Backoff]
    E -->|❌ Error| G[503 Service Unavailable]
    E -->|✅ OK| H[Llama DB]
    
    F --> I{Retry exitoso?}
    I -->|✅ Sí| H
    I -->|❌ No después<br/>de 3 intentos| G
    
    H --> J{DB disponible?}
    J -->|❌ Connection Error| K[500 Internal Server Error]
    J -->|✅ OK| L[Persiste producto]
    
    L --> M{Stock < 10?}
    M -->|✅ Sí| N[Dispara Webhook n8n]
    M -->|❌ No| O[Retorna 201 Created]
    
    N --> P{Webhook exitoso?}
    P -->|❌ Error| Q[⚠️ Log warning<br/>pero no falla request]
    P -->|✅ OK| O
    
    Q --> O
    
    style C fill:#f44336,color:#fff
    style G fill:#ff9800,color:#fff
    style K fill:#f44336,color:#fff
    style O fill:#4caf50,color:#fff
    style Q fill:#ffc107,color:#000
```

## 📊 Diagrama de Estados del Producto

```mermaid
stateDiagram-v2
    [*] --> Creating: Usuario crea producto
    Creating --> Enriching_Description: Llamando IA
    Enriching_Description --> Enriching_Category: Descripción OK
    Enriching_Category --> Persisting: Categoría OK
    Persisting --> Active: Guardado en DB
    
    Active --> Selling: Usuario simula venta
    Selling --> Active: Stock > 10
    Selling --> Low_Stock: Stock < 10
    
    Low_Stock --> Alert_Sent: Webhook OK
    Low_Stock --> Alert_Failed: Webhook Error
    
    Alert_Failed --> Low_Stock: Retry manual
    Alert_Sent --> Active: Stock reabastecido
    Alert_Sent --> Out_of_Stock: Stock = 0
    
    Out_of_Stock --> Active: Restock
    
    Enriching_Description --> Failed: IA timeout/error
    Enriching_Category --> Failed: IA timeout/error
    Persisting --> Failed: DB error
    
    Failed --> [*]: Request rechazado
    Out_of_Stock --> [*]: Producto descontinuado
```

## 🚀 Diagrama de Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                             │
│                     (Docker Host - Linux)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           Docker Compose (app-network)                  │    │
│  │                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │   Frontend   │  │   Backend    │  │ Microservice│  │    │
│  │  │    :5173     │◄─┤   :8000      │◄─┤ IA :8001    │  │    │
│  │  └──────────────┘  └──────┬───────┘  └──────┬──────┘  │    │
│  │                           │                  │          │    │
│  │                           │                  │          │    │
│  │  ┌──────────────┐  ┌──────▼───────┐  ┌─────▼──────┐  │    │
│  │  │     n8n      │◄─┤  PostgreSQL  │  │  OpenAI    │  │    │
│  │  │    :5678     │  │   :5432      │  │   API      │  │    │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │    │
│  │         │                 │                  │         │    │
│  │         │                 │                  │         │    │
│  │  ┌──────▼──────┐   ┌──────▼───────┐         │         │    │
│  │  │ n8n_data    │   │postgres_data │         │         │    │
│  │  │  (volume)   │   │   (volume)   │         │         │    │
│  │  └─────────────┘   └──────────────┘         │         │    │
│  │                                              │         │    │
│  └──────────────────────────────────────────────┼─────────┘    │
│                                                 │              │
│                                                 │ HTTPS        │
│                                                 ▼              │
│                                        ┌──────────────────┐    │
│                                        │ External Service │    │
│                                        │  (OpenAI/Gemini) │    │
│                                        └──────────────────┘    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               Puertos Expuestos al Host:                  │ │
│  │  • 5173 → Frontend (desarrollo)                          │ │
│  │  • 80   → Frontend (producción)                          │ │
│  │  • 8000 → Backend Principal                              │ │
│  │  • 8001 → Microservicio IA                               │ │
│  │  • 5678 → n8n UI                                         │ │
│  │  • 5432 → PostgreSQL (solo para debug)                   │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📈 Diagrama de Monitoreo y Observabilidad (Futuro)

```mermaid
graph TB
    subgraph "Aplicación"
        F[Frontend]
        B[Backend Principal]
        I[Microservicio IA]
        N[n8n]
    end

    subgraph "Logs"
        L[Structured Logs<br/>JSON Format]
    end

    subgraph "Métricas"
        M[Prometheus<br/>Métricas]
    end

    subgraph "Trazas"
        T[Jaeger<br/>Distributed Tracing]
    end

    subgraph "Visualización"
        G[Grafana<br/>Dashboards]
    end

    subgraph "Alertas"
        A[AlertManager<br/>Email/Slack]
    end

    F --> L
    B --> L
    I --> L
    N --> L

    F --> M
    B --> M
    I --> M

    F --> T
    B --> T
    I --> T

    L --> G
    M --> G
    T --> G

    M --> A

    style L fill:#2196f3,color:#fff
    style M fill:#e53935,color:#fff
    style T fill:#ffa726,color:#000
    style G fill:#66bb6a,color:#000
    style A fill:#ab47bc,color:#fff
```

## 🔑 Leyenda de Iconos

| Icono | Significado |
|-------|-------------|
| 🖥️ | Frontend / UI |
| ⚙️ | Backend / API |
| 🤖 | Servicio IA / ML |
| 🔄 | Automatización / Workflow |
| 🗄️ | Base de Datos |
| 🧠 | LLM / IA Externa |
| 📊 | API Mock / Testing |
| 👤 | Usuario Final |
| 🚨 | Alerta / Notificación |
| ⏱️ | Timeout / Retry |
| ✅ | Éxito / OK |
| ❌ | Error / Fallo |
| ⚠️ | Warning / Degradado |

---

**Nota**: Para visualizar los diagramas Mermaid, puedes usar:
- GitHub (renderiza automáticamente en README.md)
- VS Code con extensión "Markdown Preview Mermaid Support"
- Mermaid Live Editor: https://mermaid.live/
- Herramientas de documentación como Docusaurus, GitBook, etc.
