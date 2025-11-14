import { Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import './App.css';
import TopNav from './components/TopNav.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import PublicCatalog from './pages/PublicCatalog.jsx';
import Login from './pages/Login.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import initialProducts from './data/initialProducts.js';

const PRODUCTS_STORAGE_KEY = 'neostore.products';
const SESSION_STORAGE_KEY = 'neostore.session';
const ADMIN_CREDENTIALS = {
  email: 'admin@neostore.com',
  password: 'neostore-2025'
};

const loadFromStorage = (key, fallback) => {
  if (typeof window === 'undefined') {
    return fallback;
  }
  try {
    const stored = window.localStorage.getItem(key);
    return stored ? JSON.parse(stored) : fallback;
  } catch (error) {
    console.warn('No se pudo leer del almacenamiento local', error);
    return fallback;
  }
};

const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `prd-${Date.now()}`;
};

const normalizeProduct = (product) => {
  if (!product) {
    return null;
  }

  const tags = Array.isArray(product.tags)
    ? product.tags
    : Array.isArray(product.keywords)
      ? product.keywords
      : [];

  return {
    id: product.id || generateId(),
    name: product.name || 'Nuevo producto',
    description: product.description || 'Describe tu producto para destacar beneficios.',
    price: typeof product.price === 'number' ? product.price : Number(product.price ?? 0) || 0,
    stock: Number.isFinite(product.stock) ? product.stock : Number(product.stock ?? 0) || 0,
    category: product.category || 'General',
    tags,
    status: product.status || 'Publicado',
    cover: product.cover || '',
    highlight: Boolean(product.highlight),
    createdAt: product.createdAt || new Date().toISOString()
  };
};

const bootstrapProducts = () => {
  const stored = loadFromStorage(PRODUCTS_STORAGE_KEY, null);
  if (Array.isArray(stored) && stored.length) {
    return stored.map(normalizeProduct).filter(Boolean);
  }
  return initialProducts.map(normalizeProduct);
};

function App() {
  const [products, setProducts] = useState(bootstrapProducts);
  const [session, setSession] = useState(() => loadFromStorage(SESSION_STORAGE_KEY, null));

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(PRODUCTS_STORAGE_KEY, JSON.stringify(products));
    }
  }, [products]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (session) {
      window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
    } else {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
    }
  }, [session]);

  const isAuthenticated = Boolean(session);

  const handleLogin = ({ email, password }) => {
    if (email === ADMIN_CREDENTIALS.email && password === ADMIN_CREDENTIALS.password) {
      const payload = { email, loggedAt: new Date().toISOString() };
      setSession(payload);
      return { success: true };
    }
    return { success: false, message: 'Credenciales inválidas. Intenta de nuevo.' };
  };

  const handleLogout = () => {
    setSession(null);
  };

  const handleCreateProduct = (data) => {
    const newProduct = normalizeProduct({
      ...data,
      id: generateId(),
      createdAt: new Date().toISOString()
    });
    setProducts((prev) => [newProduct, ...prev]);
  };

  const handleUpdateProduct = (productId, data) => {
    setProducts((prev) =>
      prev.map((product) =>
        product.id === productId
          ? normalizeProduct({ ...product, ...data, id: product.id, createdAt: product.createdAt })
          : product
      )
    );
  };

  const handleDeleteProduct = (productId) => {
    setProducts((prev) => prev.filter((product) => product.id !== productId));
  };

  return (
    <div className="app-shell">
      <TopNav isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <main className="page-wrapper">
        <Routes>
          <Route path="/" element={<PublicCatalog products={products} />} />
          <Route
            path="/login"
            element={<Login onLogin={handleLogin} isAuthenticated={isAuthenticated} />}
          />
          <Route
            path="/admin"
            element={(
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <AdminDashboard
                  products={products}
                  onCreate={handleCreateProduct}
                  onUpdate={handleUpdateProduct}
                  onDelete={handleDeleteProduct}
                />
              </ProtectedRoute>
            )}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
