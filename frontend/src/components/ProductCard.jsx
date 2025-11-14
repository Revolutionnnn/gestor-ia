const currencyFormatter = new Intl.NumberFormat('es-ES', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const ProductCard = ({ product, onSell, isSelling }) => {
  const coverImage = product.image_url || product.cover;
  const coverStyle = coverImage
    ? {
        backgroundImage: `linear-gradient(120deg, rgba(0,0,0,0.2), rgba(0,0,0,0.6)), url(${coverImage})`,
      }
    : undefined;

  const tags = Array.isArray(product.keywords)
    ? product.keywords
    : Array.isArray(product.tags)
      ? product.tags
      : [];

  const statusLabel = product.stock > 0 ? 'Disponible' : 'Sin stock';
  const statusClass = product.stock > 0 ? 'status-publicado' : 'status-borrador';
  const priceLabel = currencyFormatter.format(product.price || 0);
  const categoryLabel = product.category || 'Sin categoría';
  const isDisabled = !onSell || product.stock <= 0 || isSelling || product.is_active === false;
  const buttonLabel = isSelling ? 'Procesando…' : product.stock <= 0 ? 'Sin stock' : 'Comprar ahora';
  const description = product.description || 'Producto disponible en Orquestia Store con envío inmediato.';

  return (
    <article className={`product-card ${product.highlight ? 'product-card--featured' : ''}`}>
      <div className="product-card__media" style={coverStyle}>
        <span className="badge">{categoryLabel}</span>
      </div>
      <div className="product-card__content">
        <div className="product-card__meta">
          <span className={`status-pill ${statusClass}`}>
            {statusLabel}
          </span>
          <span className="price">{priceLabel}</span>
        </div>
        <h3>{product.name}</h3>
  <p>{description}</p>
        <div className="tag-list">
          {tags.length > 0 ? (
            tags.map((tag) => (
              <span key={tag} className="tag-chip">
                {tag}
              </span>
            ))
          ) : (
            <span className="tag-chip">Catálogo Orquestia</span>
          )}
        </div>
        <div className="product-card__footer">
          <span>Stock: {product.stock}</span>
          <button
            type="button"
            className="primary-btn primary-btn--sm"
            disabled={isDisabled}
            onClick={onSell}
          >
            {buttonLabel}
          </button>
        </div>
      </div>
    </article>
  );
};

export default ProductCard;
