import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminProductForm from '../components/AdminProductForm.jsx';
import Modal from '../components/Modal.jsx';
import api from '../services/api.js';

const AdminDashboard = ({ onLogout }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

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
      setIsCreateModalOpen(false);
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
        <section className="panel panel-cta">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Productos asistidos por IA</p>
              <h2>Crear nuevo producto</h2>
              <p className="muted">Lanza un artículo en cuestión de segundos y deja que la IA complete los campos opcionales.</p>
            </div>
            <div className="panel-header__actions">
              <button type="button" className="primary-btn" onClick={() => setIsCreateModalOpen(true)}>
                Nuevo producto
              </button>
              <button type="button" className="ghost-btn" onClick={fetchProducts} disabled={loading}>
                {loading ? 'Actualizando…' : 'Refrescar inventario'}
              </button>
            </div>
          </div>
          <div className="panel-cta__grid">
            <article className="panel-cta__item">
              <strong>Descripción automática</strong>
              <p className="muted">Sin descripción, la IA genera una ficha atractiva usando el nombre y keywords.</p>
            </article>
            <article className="panel-cta__item">
              <strong>Categorías sugeridas</strong>
              <p className="muted">No recuerdas la categoría ideal? la IA propone la mejor opción.</p>
            </article>
            <article className="panel-cta__item">
              <strong>Visibilidad controlada</strong>
              <p className="muted">Activa o pausa el producto cuando lo necesites, sin perder datos.</p>
            </article>
          </div>
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

        <Modal
          isOpen={isCreateModalOpen}
          title="Crear nuevo producto"
          subtitle="Completa los campos obligatorios y deja que la IA termine el resto."
          onClose={() => setIsCreateModalOpen(false)}
          size="lg"
        >
          <AdminProductForm
            title="Ficha del producto"
            submitLabel="Crear producto"
            onSubmit={handleCreate}
            onCancel={() => setIsCreateModalOpen(false)}
          />
        </Modal>

        <Modal
          isOpen={Boolean(editingProduct)}
          title={editingProduct ? `Editar ${editingProduct.name}` : 'Editar producto'}
          subtitle="Actualiza el inventario, precios o estado y guarda los cambios."
          onClose={() => setEditingProduct(null)}
          size="lg"
        >
          {editingProduct && (
            <AdminProductForm
              title="Actualizar datos"
              initialData={editingProduct}
              submitLabel="Guardar cambios"
              onSubmit={(payload) => handleUpdate(editingProduct.id, payload)}
              onCancel={() => setEditingProduct(null)}
            />
          )}
        </Modal>
      </div>
    </div>
  );
};

export default AdminDashboard;
