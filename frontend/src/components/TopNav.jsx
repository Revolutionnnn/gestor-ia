import { NavLink, useNavigate } from 'react-router-dom';

const TopNav = ({ isAuthenticated, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/', { replace: true });
  };

  return (
    <header className="top-nav">
      <button type="button" className="brand-mark" onClick={() => navigate('/')}> 
        <span className="brand-mark__prefix">neo</span>
        <span className="brand-mark__suffix">store</span>
      </button>
      <nav className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
          Catálogo
        </NavLink>
        <NavLink to="/admin" className={({ isActive }) => (isActive ? 'active' : undefined)}>
          Panel
        </NavLink>
      </nav>
      <div className="nav-actions">
        {isAuthenticated ? (
          <button type="button" className="ghost-btn" onClick={handleLogout}>
            Cerrar sesión
          </button>
        ) : (
          <NavLink
            to="/login"
            className={({ isActive }) => `primary-btn ghost ${isActive ? 'active' : ''}`.trim()}
          >
            Iniciar sesión
          </NavLink>
        )}
      </div>
    </header>
  );
};

export default TopNav;
