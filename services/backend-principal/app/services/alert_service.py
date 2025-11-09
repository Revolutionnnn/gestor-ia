import os

import httpx

from ..config import logger
from ..constants import MOCK_PRICE_URL, OPENAI_MODEL, REQUEST_TIMEOUT

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


async def fetch_mock_price() -> float:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(MOCK_PRICE_URL)
        return response.json().get("price", 99.99)


def build_alert_prompt(product_name: str, stock: int, price: float) -> str:
    return f"""Genera un mensaje de alerta de stock bajo profesional.

Producto: {product_name}
Stock actual: {stock}
Precio sugerido proveedor: ${price}

El mensaje debe ser conciso (2-3 líneas) y profesional."""


async def generate_alert_message_with_ai(prompt: str) -> str:
    if GOOGLE_API_KEY:
        return await _generate_with_gemini(prompt)
    elif OPENAI_API_KEY:
        return await _generate_with_openai(prompt)
    return None


async def _generate_with_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    return response.text


async def _generate_with_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Eres un asistente profesional."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content


def create_default_alert_message(
    product_name: str, stock: int, price: float
) -> str:
    return (
        f"⚠️ Stock bajo: {product_name} tiene solo "
        f"{stock} unidades. Precio proveedor: ${price}"
    )


def print_alert_console(
    product_id: str, product_name: str, stock: int, price: float, message: str
):
    print("\n" + "=" * 80)
    print("⚠️  ALERTA: STOCK BAJO DETECTADO")
    print("=" * 80)
    print(f"Producto ID: {product_id}")
    print(f"Nombre: {product_name}")
    print(f"Stock actual: {stock} unidades")
    print(f"Precio sugerido: ${price}")
    print("\nMensaje de alerta:")
    print(f"{message.strip()}")
    print("=" * 80 + "\n")


async def send_low_stock_alert(
    product_id: str, product_name: str, current_stock: int
) -> bool:
    try:
        mock_price = await fetch_mock_price()
        prompt = build_alert_prompt(product_name, current_stock, mock_price)

        alert_message = await generate_alert_message_with_ai(prompt)
        if not alert_message:
            alert_message = create_default_alert_message(
                product_name, current_stock, mock_price
            )

        print_alert_console(
            product_id, product_name, current_stock, mock_price, alert_message
        )

        logger.warning(
            "low_stock_alert",
            product_id=product_id,
            product_name=product_name,
            stock=current_stock,
            price=mock_price,
            message=alert_message.strip(),
        )

        return True
    except Exception as e:
        logger.error("alert_error", error=str(e), product_id=product_id)
        return False
