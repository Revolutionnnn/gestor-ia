## NeoStore Frontend

Interfaz React + Vite para un ecommerce minimalista con tres vistas clave: catálogo público, login protegido y panel administrativo con CRUD mockeado. Toda la información de productos vive en el cliente y se guarda en `localStorage` para permitir iteraciones rápidas sin depender de la API.

### Características

- 🎯 **Catálogo público** con buscador, filtro por categoría y tarjetas destacadas.
- 🔐 **Login privado** que protege la vista administrativa.
- 🧩 **Panel admin** para crear, editar y eliminar productos usando estado local.
- 💾 **Persistencia local** automática para productos y sesión.

### Scripts disponibles

```bash
npm install      # instala dependencias
npm run dev      # levanta Vite en modo desarrollo
npm run build    # genera build de producción
npm run preview  # sirve la build generada
```

### Credenciales demo

- **Email:** `admin@neostore.com`
- **Contraseña:** `neostore-2025`

Puedes cambiarlas en `src/App.jsx` dentro de la constante `ADMIN_CREDENTIALS`.

### Estructura principal

- `src/pages` → vistas (`PublicCatalog`, `Login`, `AdminDashboard`).
- `src/components` → navegación, formularios y tarjetas reutilizables.
- `src/data/initialProducts.js` → productos semilla que se cargan al primer inicio.

### Próximos pasos sugeridos

1. Conectar las acciones del panel con la API real (microservicio de productos).
2. Reemplazar el login mock por el flujo del microservicio `auth`.
3. Añadir tests de integración para los formularios y rutas.
