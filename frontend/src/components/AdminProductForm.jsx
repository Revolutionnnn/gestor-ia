import { useEffect, useState } from 'react';

const emptyTemplate = {
  name: '',
  description: '',
  price: '',
  stock: '',
  category: '',
  keywords: '',
  image_url: '',
  is_active: true
};

const normalizePayload = (formValues) => {
  const keywordsArray = formValues.keywords
    ? formValues.keywords.split(',').map((kw) => kw.trim()).filter(Boolean)
    : [];

  return {
    name: formValues.name.trim(),
    keywords: keywordsArray,
    stock: Number.parseInt(formValues.stock, 10) || 0,
    price: Number.parseInt(formValues.price, 10) || 0,
    description: formValues.description?.trim() || null,
    category: formValues.category?.trim() || null,
    image_url: formValues.image_url?.trim() || null,
    is_active: Boolean(formValues.is_active)
  };
};

const AdminProductForm = ({ title, submitLabel, onSubmit, initialData, onCancel }) => {
  const [formValues, setFormValues] = useState(
    initialData
      ? { ...initialData, keywords: Array.isArray(initialData.keywords) ? initialData.keywords.join(', ') : '' }
      : emptyTemplate
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormValues({
        ...initialData,
        keywords: Array.isArray(initialData.keywords) ? initialData.keywords.join(', ') : ''
      });
    } else {
      setFormValues(emptyTemplate);
    }
  }, [initialData]);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormValues((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    const payload = normalizePayload(formValues);
    const maybePromise = onSubmit(payload);
    if (!initialData) {
      setFormValues(emptyTemplate);
    }
    Promise.resolve(maybePromise).finally(() => {
      setIsSubmitting(false);
    });
  };

  return (
    <form className="admin-form" onSubmit={handleSubmit}>
      {title && <h3>{title}</h3>}
      <div className="form-grid">
        <label>
          <span>Nombre</span>
          <input
            name="name"
            type="text"
            placeholder="Ej. Nova Air"
            value={formValues.name}
            onChange={handleChange}
            required
          />
        </label>
        <label className="full-row">
          <span>Palabras clave (separadas por coma)</span>
          <input
            name="keywords"
            type="text"
            placeholder="laptop, tecnología, profesional"
            value={formValues.keywords}
            onChange={handleChange}
            required
          />
          <small>La IA usará estas palabras para generar la descripción si no la proporcionas</small>
        </label>
        <label>
          <span>Precio (USD)</span>
          <input
            name="price"
            type="number"
            min="0"
            step="1"
            placeholder="0"
            value={formValues.price}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Stock</span>
          <input
            name="stock"
            type="number"
            min="0"
            placeholder="0"
            value={formValues.stock}
            onChange={handleChange}
            required
          />
        </label>
        <label className="full-row">
          <span>Descripción (opcional)</span>
          <textarea
            name="description"
            placeholder="Deja vacío para que la IA genere una descripción automática"
            value={formValues.description || ''}
            onChange={handleChange}
            rows={3}
          />
          <small>Si no la proporcionas, la IA la generará basándose en el nombre y palabras clave</small>
        </label>
        <label>
          <span>Categoría (opcional)</span>
          <input
            name="category"
            type="text"
            placeholder="Deja vacío para generación automática"
            value={formValues.category || ''}
            onChange={handleChange}
          />
          <small>La IA puede sugerir una categoría automáticamente</small>
        </label>
        <label>
          <span>Imagen URL (opcional)</span>
          <input
            name="image_url"
            type="url"
            placeholder="https://..."
            value={formValues.image_url || ''}
            onChange={handleChange}
          />
        </label>
        <label className="toggle">
          <input
            name="is_active"
            type="checkbox"
            checked={formValues.is_active}
            onChange={handleChange}
          />
          <span>Producto activo (visible en catálogo público)</span>
        </label>
      </div>
      <div className="form-actions">
        {onCancel && (
          <button type="button" className="ghost-btn" onClick={onCancel}>
            Cancelar
          </button>
        )}
        <button type="submit" className="primary-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando…' : submitLabel}
        </button>
      </div>
    </form>
  );
};

export default AdminProductForm;
