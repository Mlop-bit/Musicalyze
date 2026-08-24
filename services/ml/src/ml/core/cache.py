import httpx

from ml.core.config import Settings


def _values_url(settings: Settings, key: str) -> str:
    return (
        f"https://api.cloudflare.com/client/v4/accounts/{settings.kv_account_id}"
        f"/storage/kv/namespaces/{settings.kv_namespace_id}/values/{key}"
    )


def get_cached_value(key: str, settings: Settings) -> str | None:
    response = httpx.get(
        _values_url(settings, key),
        headers={"Authorization": f"Bearer {settings.kv_api_token}"},
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def set_cached_value(key: str, value: str, settings: Settings) -> None:
    response = httpx.put(
        _values_url(settings, key),
        headers={"Authorization": f"Bearer {settings.kv_api_token}"},
        content=value,
    )
    response.raise_for_status()
