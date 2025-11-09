# 🏗️ Diagramas de Arquitectura

## 📋 Estructura de Servicios

### Backend Principal
```
services/backend-principal/
├── main.py              → Entry point
├── config.py            → Configuración + Logging
├── database.py          → SQLAlchemy ORM
├── models.py            → Modelos DB
├── schemas.py           → Pydantic schemas
├── routes/
│   ├── health.py        → GET /health
│   └── products.py      → CRUD productos
└── services/
    ├── product_service.py    → Lógica de productos
    ├── alert_service.py      → Alertas de stock
    └── ia_client.py          → Cliente OpenAI
```

### Microservicio IA
```
services/microservicio-ia/
├── main.py              → Entry point
├── config.py            → Configuración
├── routes.py            → Endpoints
├── llm_service.py       → Lógica LLM
├── prompts.py           → Templates
└── models.py            → Schemas
```

## 🔄 Flujo: Crear Producto

```
CLIENT
  │
  ├─ POST /products {name, keywords, stock}
  │
  ▼
┌─────────────────────────────────┐
│   Backend Principal             │
│ ProductService.create_product() │
├─────────────────────────────────┤
│  1. Llama OpenAI → descripción  │
│  2. Llama OpenAI → categoría    │
│  3. Guarda en PostgreSQL        │
│  4. Retorna producto enriquecido│
└─────────────────────────────────┘
  │
  └─ 200 OK + producto
```

## 🚨 Flujo: Venta y Alerta

```
CLIENT
  │
  ├─ POST /products/{id}/sell
  │
  ▼
┌──────────────────────────────────┐
│   Backend Principal              │
│  routes/products.py sell_product │
├──────────────────────────────────┤
│  1. UPDATE stock -= 1            │
│  2. if stock < 10:               │
│     - Genera alerta con OpenAI   │
│     - Guarda en logs             │
│  3. Retorna nuevo stock          │
└──────────────────────────────────┘
  │
  └─ 200 OK + {new_stock}
```

## �️ Capas

```
Routes (HTTP)
    ↓
Services (Lógica)
    ↓
Models (DB)
    ↓
OpenAI SDK (IA)
```
