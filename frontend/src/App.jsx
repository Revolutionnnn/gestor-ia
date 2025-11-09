import { useState, useEffect } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ name: '', keywords: '', stock: 10 });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_URL}/products`);
      const data = await res.json();
      setProducts(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const keywords = formData.keywords.split(',').map(k => k.trim());
      const res = await fetch(`${API_URL}/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, keywords, stock: parseInt(formData.stock) })
      });
      if (res.ok) {
        setFormData({ name: '', keywords: '', stock: 10 });
        fetchProducts();
      }
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const handleSell = async (id) => {
    try {
      await fetch(`${API_URL}/products/${id}/sell`, { method: 'POST' });
      fetchProducts();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="container">
      <h1>🛒 Product Enrichment System</h1>
      
      <div className="form-section">
        <h2>➕ Añadir Producto</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Nombre del producto"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Palabras clave (separadas por comas)"
            value={formData.keywords}
            onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Stock inicial"
            value={formData.stock}
            onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
            required
            min="0"
          />
          <button type="submit" disabled={loading}>
            {loading ? '✨ Generando con IA...' : '✨ Crear Producto'}
          </button>
        </form>
      </div>

      <div className="products-section">
        <h2>📦 Productos ({products.length})</h2>
        <div className="products-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <h3>{product.name}</h3>
              <p className="description">{product.description}</p>
              <p className="category">📂 {product.category}</p>
              <div className="keywords">
                {product.keywords.map((kw, i) => (
                  <span key={i} className="keyword">{kw}</span>
                ))}
              </div>
              <div className="stock-info">
                <span className={product.stock < 10 ? 'stock-low' : 'stock-ok'}>
                  📦 Stock: {product.stock} {product.stock === 0 && '⚠️'}
                </span>
                <button onClick={() => handleSell(product.id)} disabled={product.stock === 0}>
                  {product.stock === 0 ? '❌ Agotado' : '🛒 Vender'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
