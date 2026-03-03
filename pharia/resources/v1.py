from dataclasses import dataclass
from typing import TYPE_CHECKING

from pharia.resources.connectors import Connectors
from pharia.resources.repositories import Repositories
from pharia.resources.search_stores import SearchStores
from pharia.resources.stages import Stages


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class V1:
    """V1 API namespace."""

    client: "Client"
    stages: Stages
    repositories: Repositories
    connectors: Connectors
    search_stores: SearchStores
