import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from ml.core.config import Settings
from ml.serving.api.dependencies import get_settings


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    expected = settings.api_key.get_secret_value().encode()
    if x_api_key is None or not secrets.compare_digest(x_api_key.encode(), expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing API key")
