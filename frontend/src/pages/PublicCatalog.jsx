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
    const unique = new Set(
      products
        .map((product) => product.category?.trim())
        .filter(Boolean)
    );
    return ['all', ...Array.from(unique)];
  }, [products]);

  const filteredProducts = useMemo(() => {
    const normalizedTerm = searchTerm.trim().toLowerCase();
    return products.filter((product) => {
      const name = product.name?.toLowerCase() ?? '';
      const description = product.description?.toLowerCase() ?? '';
      const matchesSearch =
        normalizedTerm.length === 0 ||
        name.includes(normalizedTerm) ||
        description.includes(normalizedTerm);

      const normalizedCategory = product.category?.trim();
      const matchesCategory =
        selectedCategory === 'all' ||
        (normalizedCategory && normalizedCategory === selectedCategory);

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
        <div className="filter-field filter-field--search">
          <label htmlFor="catalog-search">
            <span className="filter-field__label">Buscar productos</span>
            <span className="filter-field__hint">Nombre o descripción</span>
          </label>
          <div className="input-shell">
            <span className="input-shell__icon" aria-hidden="true">🔍</span>
            <input
              id="catalog-search"
              type="search"
              placeholder="Escribe para filtrar el catálogo"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </div>
        </div>
        <div className="filter-field">
          <label htmlFor="category-filter">
            <span className="filter-field__label">Filtrar por categoría</span>
            <span className="filter-field__hint">Selecciona una opción específica</span>
          </label>
          <div className="input-shell">
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
