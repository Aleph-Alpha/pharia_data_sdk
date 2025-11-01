from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.resources.search_stores import SearchStores


@dataclass
class Beta:
    """Beta API namespace."""

    client: "Client"
    search_stores: SearchStores
