import { useEffect, useMemo, useState } from 'react';
import ProductCard from '../components/ProductCard.jsx';
import api from '../services/api.js';

const PublicCatalog = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.products.listPublic();
        setProducts(data);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('No se pudieron cargar los productos');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const categories = useMemo(() => {
    const unique = new Set(products.map((product) => product.category));
    return ['all', ...Array.from(unique)];
  }, [products]);

  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [products, searchTerm, selectedCategory]);

  if (loading) {
    return (
      <div className="page page-public">
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Cargando productos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page page-public">
        <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page page-public">
      <section className="hero">
        <div>
          <p className="eyebrow">Colección otoño 2025</p>
          <h1>
            Ecommerce minimalista para productos con carácter
          </h1>
          <p className="lead">
            Gestiona tu catálogo, destaca lanzamientos y ofrece experiencias modernas en minutos.
          </p>
        </div>
        <div className="hero-card">
          <p>Inventario activo</p>
          <h2>{products.length}</h2>
          <span>productos disponibles</span>
        </div>
      </section>

      <section className="filters-panel">
        <div className="search-bar">
          <input
            type="search"
            placeholder="Buscar por nombre o descripción"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>
        <div className="category-selector">
          <label htmlFor="category-filter">Categoría</label>
          <select
            id="category-filter"
            value={selectedCategory}
            onChange={(event) => setSelectedCategory(event.target.value)}
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category === 'all' ? 'Todas' : category}
              </option>
            ))}
          </select>
        </div>
      </section>

      {filteredProducts.length === 0 ? (
        <div className="empty-state">
          <h3>No encontramos resultados</h3>
          <p>Prueba con otra palabra clave o cambia la categoría seleccionada.</p>
        </div>
      ) : (
        <section className="catalog-grid">
          {filteredProducts.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </section>
      )}
    </div>
  );
};

export default PublicCatalog;
