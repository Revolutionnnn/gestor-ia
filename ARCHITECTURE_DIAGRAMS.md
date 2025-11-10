# 🏗️ Diagramas de Arquitectura

## 📋 Estructura de Servicios

### Backend Principal
```
services/backend-principal/
├── main.py              → Entry point
├── config.py            → Configuración + Logging
├── database.py          → SQLAlchemy ORM
├── models.py            → Modelos DB
├── routes/
│   ├── health.py        → GET /health
│   └── products.py      → CRUD productos
└── services/
    ├── product_service.py    → Lógica de productos
    └── ia_client.py          → Cliente IA
```

### Microservicio IA
```
services/microservicio-ia/
├── main.py              → Entry point
├── llm_service.py       → Generación con LLM
└── routes.py            → Endpoints
```

### Microservicio Alertas
```
services/microservicio-alertas/
├── main.py              → Entry point
├── langchain_service.py → Lógica de alertas
└── routes.py            → Endpoints
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
┌────────────────────────────┐
│  Backend Principal         │
│  sell_product()            │
├────────────────────────────┤
│  1. UPDATE stock -= 1      │
│  2. if stock < 10:         │
│     - POST a Microservicio │
│       Alertas              │
│  3. Retorna nuevo stock    │
└────────────────────────────┘
  │
  ├─ Notifica a Microservicio Alertas
  │
  ▼
┌────────────────────────────┐
│  Microservicio Alertas     │
│  Genera + Guarda alerta    │
└────────────────────────────┘
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
