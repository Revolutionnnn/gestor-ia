const ProductCard = ({ product }) => {
  const coverStyle = product.cover
    ? { backgroundImage: `linear-gradient(120deg, rgba(0,0,0,0.1), rgba(0,0,0,0.5)), url(${product.cover})` }
    : undefined;

  return (
    <article className={`product-card ${product.highlight ? 'product-card--featured' : ''}`}>
      <div className="product-card__media" style={coverStyle}>
        <span className="badge">{product.category}</span>
      </div>
      <div className="product-card__content">
        <div className="product-card__meta">
          <span className={`status-pill status-${product.status?.toLowerCase() || 'publicado'}`}>
            {product.status}
          </span>
          <span className="price">${product.price.toFixed(2)}</span>
        </div>
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        <div className="tag-list">
          {product.tags?.map((tag) => (
            <span key={tag} className="tag-chip">
              {tag}
            </span>
          ))}
        </div>
        <div className="product-card__footer">
          <span>Stock: {product.stock}</span>
          <button type="button" className="ghost-btn ghost-sm" disabled>
            Próximamente
          </button>
        </div>
      </div>
    </article>
  );
};

export default ProductCard;
