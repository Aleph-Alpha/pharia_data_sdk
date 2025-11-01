import os
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Optional

import httpx

from pharia.resources.connectors import Connectors
from pharia.resources.datasets import Datasets
from pharia.resources.files import Files
from pharia.resources.repositories import Repositories
from pharia.resources.stages import Stages


@dataclass
class Client:
    """
    Async client for Pharia Data API.

    Configuration is read from environment variables by default:
    - PHARIA_DATA_API_BASE_URL: API base URL
    - PHARIA_API_KEY: API authentication key

    You can also pass values directly to override environment variables.

    Examples:
        # Using environment variables (recommended)
        client = Client()

        # Explicit configuration
        client = Client(
            base_url="https://api.example.com",
            api_key="your-key"
        )
    """

    base_url: str = ""
    api_key: str = ""
    timeout: float = 600.0
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.base_url = self.base_url or os.getenv("PHARIA_DATA_API_BASE_URL", "")
        self.api_key = self.api_key or os.getenv("PHARIA_API_KEY", "")
        if not self.base_url:
            raise ValueError("Either pass a base_url paramater or set $PHARIA_DATA_API_BASE_URL!")
        if not self.api_key:
            raise ValueError("Either pass an api_key parameter or set $PHARIA_API_KEY")
        self.base_url = self.base_url.rstrip("/")
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def with_options(
        self, api_key: str = "", timeout: float = 0.0, headers: dict[str, str] | None = None
    ) -> "Client":
        """
        Create a new client with updated options.
        """
        return Client(
            base_url=self.base_url,
            api_key=api_key or self.api_key,
            timeout=timeout or self.timeout,
            headers=headers or deepcopy(self.headers),
        )

    @property
    def stages(self) -> Stages:
        return Stages(self)

    @property
    def files(self) -> Files:
        return Files(self)

    @property
    def datasets(self) -> Datasets:
        return Datasets(self)

    @property
    def repositories(self) -> Repositories:
        return Repositories(self)

    @property
    def connectors(self) -> Connectors:
        return Connectors(self)

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float = 0.0,
    ) -> Any:
        """
        Make an HTTP request to the API.
        """
        url = f"{self.base_url}{path}"
        request_headers = dict(self.headers)
        request_headers["Content-Type"] = "application/json"
        timeout_value = timeout or self.timeout or 30.0

        async with httpx.AsyncClient(timeout=timeout_value) as client:
            response = await client.request(
                method=method, url=url, params=params, json=json, headers=request_headers
            )

            response.raise_for_status()

            if response.status_code == 204:
                return None

            return response.json()
