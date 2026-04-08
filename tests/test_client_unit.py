"""Unit tests for Client configuration (no live API)."""

import pytest

from pharia import Client


class TestClientValidation:
    def test_missing_base_url_message(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("PHARIA_DATA_API_BASE_URL", raising=False)
        monkeypatch.setenv("PHARIA_API_KEY", "test-key")
        with pytest.raises(ValueError, match="base_url parameter"):
            Client(base_url="", api_key="test-key")

    def test_missing_api_key_message(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PHARIA_DATA_API_BASE_URL", "https://api.example.com")
        monkeypatch.delenv("PHARIA_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key parameter"):
            Client(base_url="https://api.example.com", api_key="")
