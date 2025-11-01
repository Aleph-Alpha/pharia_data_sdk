from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.resources.connectors import Connectors
from pharia.resources.datasets import Datasets
from pharia.resources.files import Files
from pharia.resources.repositories import Repositories
from pharia.resources.stages import Stages


@dataclass
class V1:
    """V1 API namespace."""

    client: "Client"
    stages: Stages
    files: Files
    datasets: Datasets
    repositories: Repositories
    connectors: Connectors
