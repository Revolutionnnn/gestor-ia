def build_description_prompt(product_name: str, keywords: list[str]) -> str:
    keywords_str = ", ".join(keywords)
    return f"""Eres un copywriter experto en e-commerce. Genera una descripción atractiva y persuasiva para el siguiente producto:

Nombre del Producto: {product_name}
Características Clave: {keywords_str}

La descripción debe:
- Tener entre 10-25 palabras
- Resaltar beneficios, no solo características técnicas
- Usar lenguaje persuasivo y emocional
- Incluir un call-to-action sutil
- Ser clara, concisa y profesional
- Enfocarse en el valor para el cliente

Genera SOLO la descripción del producto, sin título ni etiquetas adicionales."""


def build_category_prompt(product_name: str, description: str) -> str:
    return f"""Eres un experto en clasificación de productos de e-commerce. Clasifica el siguiente producto en una categoría jerárquica.

Nombre del Producto: {product_name}
Descripción: {description}

Debes responder con una categoría en formato jerárquico usando el símbolo " > " (espacio, mayor que, espacio).

Formato requerido: "Categoría Principal > Subcategoría > Categoría Específica"

Ejemplos:
- "Electrónica > Audio > Audífonos"
- "Ropa > Hombre > Camisetas"
- "Hogar > Cocina > Utensilios"
- "Deportes > Fitness > Accesorios"

Categorías principales disponibles:
- Electrónica
- Ropa
- Hogar
- Deportes
- Salud y Belleza
- Juguetes
- Libros
- Alimentos
- Mascotas
- Automotriz

Responde SOLO con la categoría en el formato indicado, sin explicaciones adicionales."""


DESCRIPTION_SYSTEM_MESSAGE = "Eres un experto en e-commerce y copywriting persuasivo."
