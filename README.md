# 🚀 E-Commerce Product Enrichment System

Sistema de automatización para enriquecimiento de productos usando IA - Prueba Técnica Orquestia

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)

## 📋 Descripción

PoC de un sistema interno que automatiza la creación y enriquecimiento de catálogos de productos para e-commerce. Un gerente de bodega solo necesita ingresar el nombre, palabras clave y stock inicial del producto. La IA genera automáticamente:

- ✅ **Descripción atractiva y vendedora** (copywriting profesional)
- ✅ **Categoría del producto** (clasificación jerárquica)
- ✅ **Alertas automáticas** cuando el stock es bajo

## 🏗️ Arquitectura

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React     │─────▶│  Backend         │─────▶│  Microservicio  │
│   Frontend  │      │  Principal       │      │  IA (FastAPI)   │
└─────────────┘      │  (FastAPI)       │      └────────┬────────┘
                     └────────┬─────────┘               │
                              │                         │
                     ┌────────▼─────────┐      ┌────────▼────────┐
                     │   PostgreSQL     │      │  OpenAI SDK     │
                     │   Database       │      │  (LLM Calls)    │
                     └──────────────────┘      └─────────────────┘
```

**Tecnologías**:
- **Frontend**: React 18 + Vite
- **Backend Principal**: FastAPI (Python 3.11+)
- **Microservicio IA**: FastAPI (Python 3.11+)
- **LLM**: OpenAI API / Gemini
- **Base de Datos**: PostgreSQL 16
- **Contenerización**: Docker + Docker Compose

## 📚 Documentación

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Decisiones arquitectónicas (ADRs), trade-offs, estrategias de resiliencia
- **[DIAGRAMS.md](./DIAGRAMS.md)** - Diagramas visuales (Mermaid) de arquitectura y flujos
- **[openapi-specs.yaml](./openapi-specs.yaml)** - Contratos API completos (OpenAPI 3.0)
- **[database-schema.sql](./database-schema.sql)** - Esquema de base de datos, índices, triggers

## ⚡ Quick Start

### Prerrequisitos

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- API Key de OpenAI o Google Gemini

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd proyecto-ia
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu API key
nano .env  # o vim, code, etc.
```

**IMPORTANTE**: Configurar al menos:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Levantar el Sistema Completo

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

### 4. Verificar que Todo Esté Funcionando

```bash
# Health checks
curl http://localhost:8000/health  # Backend Principal
curl http://localhost:8001/health  # Microservicio IA

# Ver estado de servicios
docker-compose ps
```

### 5. Acceder a las Interfaces

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| 🖥️ **Frontend (UI)** | http://localhost:5173 | - |
| ⚙️ **Backend API Docs** | http://localhost:8000/docs | - |
| 🤖 **Microservicio IA Docs** | http://localhost:8001/docs | - |
| ️ **PostgreSQL** | localhost:5432 | postgres / postgres_password |

## 🎯 Uso del Sistema

### Desde la UI (Recomendado)

1. Abre http://localhost:5173
2. Ve a "Añadir Producto"
3. Completa el formulario:
   - **Nombre**: "Smartwatch Deportivo"
   - **Palabras Clave**: "GPS, resistente al agua, monitor cardíaco"
   - **Stock Inicial**: 50
4. Haz clic en "Crear Producto"
5. Espera ~5-10 segundos mientras la IA genera contenido
6. ¡Listo! Verás el producto con descripción y categoría generadas

### Simular Venta y Alerta de Stock

1. En la lista de productos, haz clic en "Simular Venta" varias veces
2. Cuando el stock baje de 10 unidades, se disparará automáticamente una alerta registrada en la base de datos

### Desde la API (Postman / cURL)

```bash
# Crear producto
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Audífonos Bluetooth",
    "keywords": ["negro", "inalámbrico", "noise-cancelling"],
    "stock": 25
  }'

# Listar productos
curl http://localhost:8000/products

# Simular venta
curl -X POST http://localhost:8000/products/{product_id}/sell
```

## 🐳 Comandos Docker Útiles

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: borra la DB)
docker-compose down -v

# Ver logs de un servicio específico
docker-compose logs -f backend-principal
docker-compose logs -f microservicio-ia

# Reconstruir imágenes
docker-compose build --no-cache

# Reiniciar un servicio específico
docker-compose restart backend-principal

# Ejecutar comandos dentro de un contenedor
docker-compose exec backend-principal sh
docker-compose exec postgres psql -U postgres -d ecommerce_db

# Ver recursos consumidos
docker stats
```

## 🧪 Testing

### Health Checks

```bash
# Backend Principal
curl http://localhost:8000/health

# Microservicio IA
curl http://localhost:8001/health
```

### Tests Automatizados

```bash
# Entrar al contenedor del backend
docker-compose exec backend-principal sh

# Ejecutar tests
pytest tests/ -v
pytest tests/test_products.py -v
```

##  Troubleshooting

### Problema: "Microservicio IA no responde"

```bash
# Ver logs
docker-compose logs -f microservicio-ia

# Verificar que tenga API key configurada
docker-compose exec microservicio-ia env | grep OPENAI_API_KEY

# Reiniciar el servicio
docker-compose restart microservicio-ia
```

### Problema: "Error conectando a la base de datos"

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Conectarse manualmente
docker-compose exec postgres psql -U postgres -d ecommerce_db
```

### Problema: "Frontend muestra error CORS"

Verificar en `.env`:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Problema: "La IA está muy lenta"

- OpenAI puede tardar 5-10 segundos en generar contenido
- Considera usar `gpt-3.5-turbo` en lugar de `gpt-4` para mayor velocidad:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

## 🔐 Seguridad

⚠️ **IMPORTANTE - Este es un PoC**:

- ❌ No hay autenticación de usuarios
- ❌ No usar en producción sin hardening
- ❌ API keys expuestas en .env (usar secrets manager en prod)

## 📈 Métricas y Observabilidad

### Logs Estructurados

Todos los servicios generan logs en formato JSON:

```bash
docker-compose logs -f backend-principal | grep "product_created"
docker-compose logs -f microservicio-ia | grep "llm_request"
```

### Health Checks

```bash
# Verificar estado de todos los servicios
curl http://localhost:8000/health | jq
curl http://localhost:8001/health | jq
```

## 🤝 Contribución

Este es un proyecto de prueba técnica. Para sugerencias o mejoras:

1. Fork el repositorio
2. Crea una branch (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -am 'Añadir feature'`)
4. Push a la branch (`git push origin feature/mejora`)
5. Abre un Pull Request

Desarrollado con ❤️ para la prueba técnica de Orquestia
