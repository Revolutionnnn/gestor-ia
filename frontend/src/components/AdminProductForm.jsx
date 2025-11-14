import { useEffect, useState } from 'react';

const emptyTemplate = {
  name: '',
  description: '',
  price: '',
  stock: '',
  category: '',
  tags: '',
  status: 'Publicado',
  cover: '',
  highlight: false
};

const normalizePayload = (formValues) => {
  const tagsArray = formValues.tags
    ? formValues.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
    : [];

  return {
    name: formValues.name.trim(),
    description: formValues.description.trim(),
    price: Number.parseFloat(formValues.price) || 0,
    stock: Number.parseInt(formValues.stock, 10) || 0,
    category: formValues.category.trim(),
    tags: tagsArray,
    status: formValues.status,
    cover: formValues.cover.trim(),
    highlight: Boolean(formValues.highlight)
  };
};

const AdminProductForm = ({ title, submitLabel, onSubmit, initialData, onCancel }) => {
  const [formValues, setFormValues] = useState(
    initialData
      ? { ...initialData, tags: Array.isArray(initialData.tags) ? initialData.tags.join(', ') : '' }
      : emptyTemplate
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormValues({
        ...initialData,
        tags: Array.isArray(initialData.tags) ? initialData.tags.join(', ') : ''
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
        <label>
          <span>Categoría</span>
          <input
            name="category"
            type="text"
            placeholder="Ej. Audio"
            value={formValues.category}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Precio (USD)</span>
          <input
            name="price"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
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
          <span>Descripción</span>
          <textarea
            name="description"
            placeholder="Agrega un copy breve y atractivo"
            value={formValues.description}
            onChange={handleChange}
            rows={3}
            required
          />
        </label>
        <label className="full-row">
          <span>Etiquetas (separadas por coma)</span>
          <input
            name="tags"
            type="text"
            placeholder="Bluetooth, ANC, Carga rápida"
            value={formValues.tags}
            onChange={handleChange}
          />
        </label>
        <label>
          <span>Estado</span>
          <select name="status" value={formValues.status} onChange={handleChange}>
            <option value="Publicado">Publicado</option>
            <option value="Borrador">Borrador</option>
            <option value="Archivado">Archivado</option>
          </select>
        </label>
        <label>
          <span>Imagen destacada (URL)</span>
          <input
            name="cover"
            type="url"
            placeholder="https://..."
            value={formValues.cover}
            onChange={handleChange}
          />
        </label>
        <label className="toggle">
          <input
            name="highlight"
            type="checkbox"
            checked={formValues.highlight}
            onChange={handleChange}
          />
          <span>Destacar en la vista pública</span>
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
