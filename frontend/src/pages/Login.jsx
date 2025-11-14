import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = ({ onLogin, isAuthenticated }) => {
  const navigate = useNavigate();
  const [formValues, setFormValues] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/admin', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');
    
    try {
      const result = await onLogin(formValues);
      
      if (result.success) {
        navigate('/admin', { replace: true });
      } else {
        setError(result.message || 'Error al iniciar sesión');
      }
    } catch {
      setError('Error de conexión. Intenta de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page page-login">
      <section className="login-card">
        <p className="eyebrow">Acceso privado</p>
        <h1>Inicia sesión</h1>
        <p className="muted">Usa las credenciales internas para acceder al panel administrativo.</p>
        <form onSubmit={handleSubmit}>
          <label>
            <span>Email</span>
            <input
              type="email"
              name="email"
              placeholder="admin@neostore.com"
              value={formValues.email}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            <span>Contraseña</span>
            <input
              type="password"
              name="password"
              placeholder="********"
              value={formValues.password}
              onChange={handleChange}
              required
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button type="submit" className="primary-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Validando…' : 'Entrar al panel'}
          </button>
        </form>
        <div className="login-hint">
          <p>Demo rápida:</p>
          <code>admin@neostore.com / neostore-2025</code>
        </div>
      </section>
    </div>
  );
};

export default Login;
