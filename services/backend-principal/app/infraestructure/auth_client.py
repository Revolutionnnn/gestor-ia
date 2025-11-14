import httpx

from ..config import AUTH_SERVICE_URL, logger

VERIFY_ENDPOINT = "/auth/verify"
DEFAULT_TIMEOUT = 5.0


def _build_verify_url() -> str:
    return f"{AUTH_SERVICE_URL.rstrip('/')}{VERIFY_ENDPOINT}"


async def verify_token(
    token: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict | None:
    if not token:
        return None

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                _build_verify_url(),
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.TimeoutException:
        logger.error("auth_service_timeout", url=AUTH_SERVICE_URL)
        return None
    except httpx.HTTPError as exc:
        logger.error("auth_service_error", error=str(exc))
        return None

    if response.status_code != httpx.codes.OK:
        logger.warning(
            "token_verification_failed",
            status_code=response.status_code,
        )
        return None

    data = response.json()
    logger.info(
        "token_verified",
        username=data.get("username"),
        role=data.get("role"),
    )
    return data
