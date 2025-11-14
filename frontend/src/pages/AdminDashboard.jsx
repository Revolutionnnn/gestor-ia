import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminProductForm from '../components/AdminProductForm.jsx';
import api from '../services/api.js';

const AdminDashboard = ({ onLogout }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.productsAdmin.listAll();
      setProducts(data);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('No se pudieron cargar los productos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (productData) => {
    try {
      await api.productsAdmin.create(productData);
      await fetchProducts();
    } catch (err) {
      console.error('Error creating product:', err);
      alert('Error al crear el producto');
    }
  };

  const handleUpdate = async (productId, productData) => {
    try {
      await api.productsAdmin.update(productId, productData);
      await fetchProducts();
      setEditingProduct(null);
    } catch (err) {
      console.error('Error updating product:', err);
      alert('Error al actualizar el producto');
    }
  };

  const handleDelete = async (product) => {
    const confirmation = typeof window === 'undefined'
      ? true
      : window.confirm(`¿Eliminar "${product.name}" del catálogo?`);
    if (confirmation) {
      try {
        await api.productsAdmin.delete(product.id);
        await fetchProducts();
        if (editingProduct?.id === product.id) {
          setEditingProduct(null);
        }
      } catch (err) {
        console.error('Error deleting product:', err);
        alert('Error al eliminar el producto');
      }
    }
  };

  const handleToggleActive = async (product) => {
    try {
      if (product.is_active) {
        await api.productsAdmin.deactivate(product.id);
      } else {
        await api.productsAdmin.activate(product.id);
      }
      await fetchProducts();
    } catch (err) {
      console.error('Error toggling product status:', err);
      alert('Error al cambiar el estado del producto');
    }
  };

  const currencyFormatter = useMemo(
    () => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }),
    []
  );

  const stats = useMemo(() => {
    const totalStock = products.reduce((acc, product) => acc + product.stock, 0);
    const inventoryValue = products.reduce((acc, product) => acc + product.stock * product.price, 0);
    const highlighted = products.filter((product) => product.highlight).length;
    return { totalStock, inventoryValue, highlighted };
  }, [products]);

  return (
    <div className="page page-admin">
      <section className="page-header">
        <div>
          <p className="eyebrow">Inventario en tiempo real</p>
          <h1>Panel administrativo</h1>
          <p className="muted">Crea, actualiza o depura tu catálogo desde un único lugar.</p>
        </div>
        <div className="page-header__actions">
          <button type="button" className="ghost-btn" onClick={() => navigate('/')}>
            Ver catálogo público
          </button>
          <button type="button" className="ghost-btn" onClick={onLogout}>
            Cerrar sesión
          </button>
        </div>
      </section>

      <section className="stat-grid">
        <article className="stat-card">
          <span>Total productos</span>
          <strong>{products.length}</strong>
        </article>
        <article className="stat-card">
          <span>Stock disponible</span>
          <strong>{stats.totalStock}</strong>
        </article>
        <article className="stat-card">
          <span>Valor estimado</span>
          <strong>{currencyFormatter.format(stats.inventoryValue)}</strong>
        </article>
        <article className="stat-card">
          <span>Destacados</span>
          <strong>{stats.highlighted}</strong>
        </article>
      </section>

      <div className="admin-layout">
        <section className="panel">
          <div className="panel-header">
            <h2>Crear nuevo producto</h2>
            <p className="muted">Completa los campos y publícalo en la vista pública.</p>
          </div>
          <AdminProductForm
            submitLabel="Crear producto"
            onSubmit={handleCreate}
          />
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Productos publicados</h2>
            <p className="muted">Gestiona existencias, edita o elimina registros.</p>
          </div>
          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <p>Cargando productos...</p>
            </div>
          ) : error ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>
              <p>{error}</p>
            </div>
          ) : (
            <div className="admin-table">
              <div className="admin-table__head">
                <span>Producto</span>
                <span>Stock</span>
                <span>Estado</span>
                <span>Acciones</span>
              </div>
              {products.map((product) => (
                <div key={product.id} className="admin-table__row">
                  <div>
                    <p className="table-title">{product.name}</p>
                    <span className="muted">{product.category}</span>
                  </div>
                  <span>{product.stock} uds.</span>
                  <span className={`status-pill status-${product.is_active ? 'activo' : 'inactivo'}`}>
                    {product.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                  <div className="table-actions">
                    <button 
                      type="button" 
                      className="ghost-btn ghost-sm" 
                      onClick={() => handleToggleActive(product)}
                    >
                      {product.is_active ? 'Desactivar' : 'Activar'}
                    </button>
                    <button type="button" className="ghost-btn ghost-sm" onClick={() => setEditingProduct(product)}>
                      Editar
                    </button>
                    <button type="button" className="ghost-btn ghost-sm danger" onClick={() => handleDelete(product)}>
                      Eliminar
                    </button>
                  </div>
                </div>
              ))}
              {products.length === 0 && (
                <div className="empty-state">
                  <h3>No hay productos</h3>
                  <p>Cuando agregues uno aparecerá aquí.</p>
                </div>
              )}
            </div>
          )}
        </section>

        {editingProduct && (
          <section className="panel panel-highlight">
            <div className="panel-header">
              <h2>Editar producto</h2>
              <button type="button" className="ghost-btn" onClick={() => setEditingProduct(null)}>
                Cerrar
              </button>
            </div>
            <AdminProductForm
              initialData={editingProduct}
              submitLabel="Guardar cambios"
              onSubmit={(payload) => {
                handleUpdate(editingProduct.id, payload);
              }}
              onCancel={() => setEditingProduct(null)}
            />
          </section>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
