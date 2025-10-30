"""
Helper utilities for clean example output formatting.
"""

from typing import Any
from typing import Dict
from typing import Optional


class ExamplePrinter:
    """
    Context manager for clean example outputs.

    Usage:
        with ExamplePrinter("My Example") as p:
            p.section(1, 3, "First step")
            p.success("It worked!")
    """

    def __init__(self, title: str, footer: str = "Example completed!"):
        self.title = title
        self.footer_message = footer

    def __enter__(self):
        """Print header on enter."""
        print("\n" + "=" * 80)
        print(self.title)
        print("=" * 80)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Print footer on exit."""
        print("\n" + "=" * 80)
        print(self.footer_message)
        print("=" * 80)
        return False

    def section(self, number: int, total: int, title: str, description: str | None = None):
        """Print section header."""
        print(f"\n[{number}/{total}] {title}")
        print("-" * 80)
        if description:
            print(f"💡 {description}")

    def success(self, message: str, details: dict[str, Any] | None = None):
        """Print success message with optional details."""
        print(f"✅ {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    def error(self, message: str):
        """Print error message."""
        print(f"❌ {message}")

    def warning(self, message: str):
        """Print warning message."""
        print(f"⚠️  {message}")

    def info(self, message: str, indent: int = 0):
        """Print info message."""
        prefix = "  " * indent
        print(f"{prefix}{message}")

    def list_items(self, items: list, title: str | None = None):
        """Print a list of items."""
        if title:
            print(f"\n{title}:")
        for item in items:
            print(f"  - {item}")
