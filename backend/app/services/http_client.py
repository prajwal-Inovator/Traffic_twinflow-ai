import httpx
from typing import Any, Dict, Optional

from ..core.exceptions import TwinFlowException

DEFAULT_TIMEOUT = 60.0

class ServiceClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        service_name: str = "ExternalService",
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.service_name = service_name

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                detail = exc.response.text
                raise TwinFlowException(
                    f"{self.service_name} returned status {status}",
                    status_code=status,
                    detail=detail,
                )
            except httpx.RequestError as exc:
                raise TwinFlowException(
                    f"{self.service_name} request failed: {str(exc)}",
                    status_code=503,
                )

        return response.json()
