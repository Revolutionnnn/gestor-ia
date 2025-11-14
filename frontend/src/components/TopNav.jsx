import { useNavigate } from 'react-router-dom';

const TopNav = ({ isAuthenticated }) => {
  const navigate = useNavigate();

  const handleBrandClick = () => {
    navigate('/', { replace: true });
  };

  const handleAdminAccess = () => {
    const target = isAuthenticated ? '/admin' : '/login';
    navigate(target);
  };

  return (
    <header className="top-nav">
      <button type="button" className="brand-mark" onClick={handleBrandClick}>
        <span className="brand-mark__prefix">Orquestia</span>
        <span className="brand-mark__suffix">Store</span>
      </button>
      <div className="nav-spacer" aria-hidden="true" />
      <div className="nav-actions">
        <button type="button" className="primary-btn ghost" onClick={handleAdminAccess}>
          Área Admin
        </button>
      </div>
    </header>
  );
};

export default TopNav;
