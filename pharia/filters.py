"""Pythonic filter builder DSL for search store queries.

Provides operator overloading on ``Filter`` objects so users can write
expressive search filters instead of hand-building camelCase dicts:

    from pharia.filters import Filter, And, Or, Not, ModalityCondition

    And(Filter("category") == "science", ModalityCondition.text())
    Or(Filter("status") == "active", Filter("status") == "pending")
    Not(Filter("archived") == None)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Leaf conditions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetadataCondition:
    """A metadata filter leaf: ``{"metadata": {"field": ..., <op>: <value>}}``."""

    field: str
    operator: str
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {"metadata": {"field": self.field, self.operator: self.value}}


@dataclass(frozen=True)
class ModalityCondition:
    """A modality filter leaf: ``{"modality": "text"}``."""

    modality: str

    def to_dict(self) -> dict[str, Any]:
        return {"modality": self.modality}

    @classmethod
    def text(cls) -> ModalityCondition:
        return cls(modality="text")

    @classmethod
    def image(cls) -> ModalityCondition:
        return cls(modality="image")


Condition = MetadataCondition | ModalityCondition


# ---------------------------------------------------------------------------
# Group conditions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WithGroup:
    """AND group: ``{"with": [...]}``."""

    conditions: tuple[Condition, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"with": [c.to_dict() for c in self.conditions]}


@dataclass(frozen=True)
class WithOneOfGroup:
    """OR group: ``{"withOneOf": [...]}``."""

    conditions: tuple[Condition, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"withOneOf": [c.to_dict() for c in self.conditions]}


@dataclass(frozen=True)
class WithoutGroup:
    """NOT group: ``{"without": [...]}``."""

    conditions: tuple[Condition, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"without": [c.to_dict() for c in self.conditions]}


FilterGroup = WithGroup | WithOneOfGroup | WithoutGroup


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------


def And(*conditions: Condition) -> WithGroup:  # noqa: N802
    """Create an AND (``with``) group from one or more conditions."""
    return WithGroup(conditions=conditions)


def Or(*conditions: Condition) -> WithOneOfGroup:  # noqa: N802
    """Create an OR (``withOneOf``) group from one or more conditions."""
    return WithOneOfGroup(conditions=conditions)


def Not(*conditions: Condition) -> WithoutGroup:  # noqa: N802
    """Create a NOT (``without``) group from one or more conditions."""
    return WithoutGroup(conditions=conditions)


# ---------------------------------------------------------------------------
# Operator-overloading entry point
# ---------------------------------------------------------------------------

# Mapping from Python dunder → (numeric operator, datetime operator)
_COMPARISON_OPS: dict[str, tuple[str, str]] = {
    "__gt__": ("greaterThan", "after"),
    "__ge__": ("greaterThanOrEqualTo", "atOrAfter"),
    "__lt__": ("lessThan", "before"),
    "__le__": ("lessThanOrEqualTo", "atOrBefore"),
}


class Filter:
    """Entry point for building metadata conditions via operator overloading.

    Usage::

        Filter("priority") > 5          # greaterThan
        Filter("created") > datetime(…)  # after
        Filter("category") == "science"  # equalTo
        Filter("category") == None       # isNull
    """

    __slots__ = ("_field",)

    def __init__(self, field: str) -> None:
        self._field = field

    def __eq__(self, other: object) -> MetadataCondition:  # type: ignore[override]
        if other is None:
            return MetadataCondition(field=self._field, operator="isNull", value=True)
        return MetadataCondition(field=self._field, operator="equalTo", value=other)

    def __ne__(self, other: object) -> MetadataCondition:  # type: ignore[override]
        raise TypeError(
            "!= is not supported for Filter (no API equivalent). "
            "Use Not(Filter(field) == value) instead."
        )

    def __gt__(self, other: float | int | datetime) -> MetadataCondition:
        return self._compare("__gt__", other)

    def __ge__(self, other: float | int | datetime) -> MetadataCondition:
        return self._compare("__ge__", other)

    def __lt__(self, other: float | int | datetime) -> MetadataCondition:
        return self._compare("__lt__", other)

    def __le__(self, other: float | int | datetime) -> MetadataCondition:
        return self._compare("__le__", other)

    def _compare(self, dunder: str, other: float | int | datetime) -> MetadataCondition:
        numeric_op, datetime_op = _COMPARISON_OPS[dunder]
        if isinstance(other, datetime):
            return MetadataCondition(
                field=self._field, operator=datetime_op, value=other.isoformat()
            )
        return MetadataCondition(field=self._field, operator=numeric_op, value=other)

    def __hash__(self) -> int:
        return hash(self._field)

    def __repr__(self) -> str:
        return f"Filter({self._field!r})"


# ---------------------------------------------------------------------------
# resolve_filters — bridge between DSL objects and raw dicts
# ---------------------------------------------------------------------------


def resolve_filters(
    filters: list[FilterGroup | Condition | dict[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    """Resolve a mixed list of filter builder objects and raw dicts.

    - Builder objects (``WithGroup``, etc.) are converted via ``.to_dict()``.
    - Raw dicts are passed through unchanged.
    - Bare ``Condition`` objects are auto-wrapped in ``{"with": [...]}``.
    """
    if filters is None:
        return None

    resolved: list[dict[str, Any]] = []
    for f in filters:
        if isinstance(f, dict):
            resolved.append(f)
        elif isinstance(f, MetadataCondition | ModalityCondition):
            resolved.append({"with": [f.to_dict()]})
        elif isinstance(f, WithGroup | WithOneOfGroup | WithoutGroup):
            resolved.append(f.to_dict())
        else:
            resolved.append(f)
    return resolved
