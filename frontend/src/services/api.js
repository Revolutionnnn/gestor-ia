/**
 * API Client para el Backend Principal
 * Maneja autenticación, headers y requests HTTP
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8003';

/**
 * Obtiene el token de autenticación del localStorage
 */
const getToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * Guarda el token de autenticación
 */
const setToken = (token) => {
  localStorage.setItem('authToken', token);
};

/**
 * Elimina el token de autenticación
 */
const removeToken = () => {
  localStorage.removeItem('authToken');
};

/**
 * Obtiene datos del usuario del localStorage
 */
const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Guarda datos del usuario
 */
const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

/**
 * Elimina datos del usuario
 */
const removeUser = () => {
  localStorage.removeItem('user');
};

/**
 * Verifica si el usuario está autenticado
 */
const isAuthenticated = () => {
  return !!getToken();
};

/**
 * Verifica si el usuario es administrador
 */
const isAdmin = () => {
  const user = getUser();
  return user && user.role === 'admin';
};

/**
 * Realiza una petición HTTP
 */
const request = async (url, options = {}) => {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Agregar token si existe y no está en las opciones
  if (token && !options.skipAuth) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers,
  };
  
  try {
    const response = await fetch(url, config);
    
    // Si es 401, el token expiró
    if (response.status === 401) {
      removeToken();
      removeUser();
      window.location.href = '/login';
      throw new Error('Sesión expirada. Por favor inicia sesión nuevamente.');
    }
    
    // Si es 204 No Content, no hay cuerpo
    if (response.status === 204) {
      return null;
    }
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data.detail || `Error ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('Request error:', error);
    throw error;
  }
};

// =============================================================================
// AUTH API
// =============================================================================

export const authApi = {
  /**
   * Registra un nuevo usuario
   */
  register: async (email, password, fullName) => {
    const response = await request(`${AUTH_BASE_URL}/auth/register`, {
      method: 'POST',
      skipAuth: true,
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });
    
    // Guardar token y usuario
    if (response.access_token) {
      setToken(response.access_token);
    }
    if (response.user) {
      setUser(response.user);
    }
    
    return response;
  },
  
  /**
   * Inicia sesión
   */
  login: async (email, password) => {
    const response = await request(`${AUTH_BASE_URL}/auth/login`, {
      method: 'POST',
      skipAuth: true,
      body: JSON.stringify({ email, password }),
    });
    
    // Guardar token y usuario
    if (response.access_token) {
      setToken(response.access_token);
    }
    if (response.user) {
      setUser(response.user);
    }
    
    return response;
  },
  
  /**
   * Cierra sesión
   */
  logout: () => {
    removeToken();
    removeUser();
  },
  
  /**
   * Obtiene el token actual
   */
  getToken,
  
  /**
   * Obtiene el usuario actual
   */
  getCurrentUser: getUser,
  
  /**
   * Verifica si está autenticado
   */
  isAuthenticated,
  
  /**
   * Verifica si es admin
   */
  isAdmin,
};

// =============================================================================
// PRODUCTS API - PÚBLICO
// =============================================================================

export const productsApi = {
  /**
   * Lista productos activos (público)
   */
  listPublic: async () => {
    return request(`${API_BASE_URL}/products`, {
      method: 'GET',
      skipAuth: true,
    });
  },
  
  /**
   * Obtiene detalle de producto activo (público)
   */
  getPublic: async (productId) => {
    return request(`${API_BASE_URL}/products/${productId}`, {
      method: 'GET',
      skipAuth: true,
    });
  },
  
  /**
   * Vende un producto (requiere autenticación)
   */
  sell: async (productId) => {
    return request(`${API_BASE_URL}/products/${productId}/sell`, {
      method: 'POST',
    });
  },
};

// =============================================================================
// PRODUCTS API - ADMIN
// =============================================================================

export const productsAdminApi = {
  /**
   * Lista todos los productos (admin)
   */
  listAll: async () => {
    return request(`${API_BASE_URL}/products/admin/all`, {
      method: 'GET',
    });
  },
  
  /**
   * Obtiene cualquier producto (admin)
   */
  get: async (productId) => {
    return request(`${API_BASE_URL}/products/admin/${productId}`, {
      method: 'GET',
    });
  },
  
  /**
   * Crea un producto (admin)
   */
  create: async (productData) => {
    return request(`${API_BASE_URL}/products`, {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  },
  
  /**
   * Actualiza un producto (admin)
   */
  update: async (productId, productData) => {
    return request(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    });
  },
  
  /**
   * Elimina un producto (admin)
   */
  delete: async (productId) => {
    return request(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
    });
  },
  
  /**
   * Activa un producto (admin)
   */
  activate: async (productId) => {
    return request(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify({ is_active: true }),
    });
  },
  
  /**
   * Desactiva un producto (admin)
   */
  deactivate: async (productId) => {
    return request(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify({ is_active: false }),
    });
  },
};

// =============================================================================
// UTILIDADES
// =============================================================================

export const utils = {
  getToken,
  setToken,
  removeToken,
  getUser,
  setUser,
  removeUser,
  isAuthenticated,
  isAdmin,
};

// Exportar todo
export default {
  auth: authApi,
  products: productsApi,
  productsAdmin: productsAdminApi,
  utils,
};
