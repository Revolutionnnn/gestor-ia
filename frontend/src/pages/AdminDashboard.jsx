import { useMemo, useState } from 'react';
import AdminProductForm from '../components/AdminProductForm.jsx';

const AdminDashboard = ({ products, onCreate, onUpdate, onDelete }) => {
  const [editingProduct, setEditingProduct] = useState(null);

  const handleDelete = (product) => {
    const confirmation = typeof window === 'undefined'
      ? true
      : window.confirm(`¿Eliminar "${product.name}" del catálogo?`);
    if (confirmation) {
      onDelete(product.id);
      if (editingProduct?.id === product.id) {
        setEditingProduct(null);
      }
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
            onSubmit={onCreate}
          />
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Productos publicados</h2>
            <p className="muted">Gestiona existencias, edita o elimina registros.</p>
          </div>
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
                <span className={`status-pill status-${product.status?.toLowerCase()}`}>
                  {product.status}
                </span>
                <div className="table-actions">
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
                onUpdate(editingProduct.id, payload);
                setEditingProduct(null);
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
