import { useEffect, useState } from 'react';
import { Route, Routes, useNavigate } from 'react-router-dom';
import './App.css';
import TopNav from './components/TopNav.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import PublicCatalog from './pages/PublicCatalog.jsx';
import Login from './pages/Login.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import api from './services/api.js';

function App() {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay un token guardado al cargar la aplicación
    const authenticated = api.utils.isAuthenticated();
    setIsAuthenticated(authenticated);
    setIsLoading(false);
  }, []);

  const handleLogin = async (credentials) => {
    try {
      const response = await api.auth.login(credentials.email, credentials.password);
      
      if (response.token?.access_token) {
        setIsAuthenticated(true);
        return { success: true };
      } else {
        return { success: false, message: 'Credenciales inválidas' };
      }
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      return { 
        success: false, 
        message: error.message || 'Error al iniciar sesión' 
      };
    }
  };

  const handleLogout = () => {
    api.auth.logout();
    setIsAuthenticated(false);
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p>Cargando...</p>
      </div>
    );
  }

  return (
    <>
      <TopNav isAuthenticated={isAuthenticated} />
      <Routes>
        <Route path="/" element={<PublicCatalog />} />
        <Route 
          path="/login" 
          element={
            <Login 
              onLogin={handleLogin} 
              isAuthenticated={isAuthenticated} 
            />
          } 
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <AdminDashboard onLogout={handleLogout} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
