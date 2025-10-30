"""Utility functions for the Pharia SDK."""

from typing import Any


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_keys_to_camel_case(data: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively convert all dictionary keys from snake_case to camelCase.

    This is used to convert Python snake_case parameters to API camelCase format.
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        # Convert the key
        camel_key = to_camel_case(key)

        # Recursively convert nested dictionaries
        if isinstance(value, dict):
            result[camel_key] = convert_keys_to_camel_case(value)
        elif isinstance(value, list):
            result[camel_key] = [
                convert_keys_to_camel_case(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[camel_key] = value

    return result
