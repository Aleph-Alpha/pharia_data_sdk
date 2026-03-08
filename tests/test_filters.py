"""Unit tests for the filter builder DSL."""

from datetime import datetime

import pytest

from pharia.filters import And
from pharia.filters import Filter
from pharia.filters import MetadataCondition
from pharia.filters import ModalityCondition
from pharia.filters import Not
from pharia.filters import Or
from pharia.filters import resolve_filters


class TestMetadataCondition:
    def test_to_dict(self):
        cond = MetadataCondition(field="priority", operator="greaterThan", value=5)
        assert cond.to_dict() == {"metadata": {"field": "priority", "greaterThan": 5}}

    def test_is_null(self):
        cond = MetadataCondition(field="archived", operator="isNull", value=True)
        assert cond.to_dict() == {"metadata": {"field": "archived", "isNull": True}}


class TestModalityCondition:
    def test_text(self):
        assert ModalityCondition.text().to_dict() == {"modality": "text"}

    def test_image(self):
        assert ModalityCondition.image().to_dict() == {"modality": "image"}

    def test_custom(self):
        cond = ModalityCondition(modality="audio")
        assert cond.to_dict() == {"modality": "audio"}


class TestFilterOperators:
    def test_equal_to_string(self):
        cond = Filter("category") == "science"
        assert isinstance(cond, MetadataCondition)
        assert cond.to_dict() == {"metadata": {"field": "category", "equalTo": "science"}}

    def test_equal_to_int(self):
        cond = Filter("priority") == 5
        assert cond.to_dict() == {"metadata": {"field": "priority", "equalTo": 5}}

    def test_equal_to_bool(self):
        cond = Filter("active") == True  # noqa: E712
        assert cond.to_dict() == {"metadata": {"field": "active", "equalTo": True}}

    def test_equal_to_none_is_null(self):
        cond = Filter("archived") == None  # noqa: E711
        assert cond.to_dict() == {"metadata": {"field": "archived", "isNull": True}}

    def test_not_equal_raises(self):
        with pytest.raises(TypeError, match="!= is not supported"):
            Filter("x") != "y"  # noqa: B015

    def test_greater_than_numeric(self):
        cond = Filter("priority") > 5
        assert cond.to_dict() == {"metadata": {"field": "priority", "greaterThan": 5}}

    def test_greater_than_or_equal_numeric(self):
        cond = Filter("priority") >= 5
        assert cond.to_dict() == {"metadata": {"field": "priority", "greaterThanOrEqualTo": 5}}

    def test_less_than_numeric(self):
        cond = Filter("priority") < 10
        assert cond.to_dict() == {"metadata": {"field": "priority", "lessThan": 10}}

    def test_less_than_or_equal_numeric(self):
        cond = Filter("priority") <= 10
        assert cond.to_dict() == {"metadata": {"field": "priority", "lessThanOrEqualTo": 10}}

    def test_greater_than_datetime(self):
        dt = datetime(2024, 1, 1)
        cond = Filter("created") > dt
        assert cond.to_dict() == {"metadata": {"field": "created", "after": dt.isoformat()}}

    def test_greater_than_or_equal_datetime(self):
        dt = datetime(2024, 1, 1)
        cond = Filter("created") >= dt
        assert cond.to_dict() == {"metadata": {"field": "created", "atOrAfter": dt.isoformat()}}

    def test_less_than_datetime(self):
        dt = datetime(2024, 12, 31)
        cond = Filter("created") < dt
        assert cond.to_dict() == {"metadata": {"field": "created", "before": dt.isoformat()}}

    def test_less_than_or_equal_datetime(self):
        dt = datetime(2024, 12, 31)
        cond = Filter("created") <= dt
        assert cond.to_dict() == {"metadata": {"field": "created", "atOrBefore": dt.isoformat()}}

    def test_float_value(self):
        cond = Filter("score") > 0.5
        assert cond.to_dict() == {"metadata": {"field": "score", "greaterThan": 0.5}}


class TestFilterRepr:
    def test_repr(self):
        assert repr(Filter("category")) == "Filter('category')"


class TestGroups:
    def test_and_single(self):
        cond = Filter("category") == "science"
        group = And(cond)
        assert group.to_dict() == {
            "with": [{"metadata": {"field": "category", "equalTo": "science"}}]
        }

    def test_and_multiple(self):
        a = Filter("category") == "science"
        b = Filter("priority") > 5
        group = And(a, b)
        result = group.to_dict()
        assert result == {
            "with": [
                {"metadata": {"field": "category", "equalTo": "science"}},
                {"metadata": {"field": "priority", "greaterThan": 5}},
            ]
        }

    def test_and_with_modality(self):
        a = Filter("category") == "science"
        b = ModalityCondition.text()
        group = And(a, b)
        assert group.to_dict() == {
            "with": [
                {"metadata": {"field": "category", "equalTo": "science"}},
                {"modality": "text"},
            ]
        }

    def test_or(self):
        a = Filter("status") == "active"
        b = Filter("status") == "pending"
        group = Or(a, b)
        assert group.to_dict() == {
            "withOneOf": [
                {"metadata": {"field": "status", "equalTo": "active"}},
                {"metadata": {"field": "status", "equalTo": "pending"}},
            ]
        }

    def test_not_single(self):
        cond = Filter("archived") == None  # noqa: E711
        group = Not(cond)
        assert group.to_dict() == {"without": [{"metadata": {"field": "archived", "isNull": True}}]}

    def test_not_multiple(self):
        a = Filter("archived") == None  # noqa: E711
        b = Filter("deleted") == None  # noqa: E711
        group = Not(a, b)
        assert group.to_dict() == {
            "without": [
                {"metadata": {"field": "archived", "isNull": True}},
                {"metadata": {"field": "deleted", "isNull": True}},
            ]
        }

    def test_three_element_and(self):
        a = Filter("cat") == "science"
        b = Filter("priority") > 5
        c = ModalityCondition.text()
        group = And(a, b, c)
        result = group.to_dict()
        assert len(result["with"]) == 3


class TestResolveFilters:
    def test_none_returns_none(self):
        assert resolve_filters(None) is None

    def test_empty_list(self):
        assert resolve_filters([]) == []

    def test_builder_objects(self):
        group = And(Filter("category") == "science")
        result = resolve_filters([group])
        assert result == [{"with": [{"metadata": {"field": "category", "equalTo": "science"}}]}]

    def test_raw_dicts_passthrough(self):
        raw = {"with": [{"metadata": {"field": "category", "equalTo": "science"}}]}
        result = resolve_filters([raw])
        assert result == [raw]

    def test_mixed_builder_and_dicts(self):
        group = And(Filter("priority") > 5)
        raw = {"without": [{"modality": "image"}]}
        result = resolve_filters([group, raw])
        assert len(result) == 2
        assert result[0] == {"with": [{"metadata": {"field": "priority", "greaterThan": 5}}]}
        assert result[1] == raw

    def test_bare_condition_auto_wraps(self):
        cond = Filter("category") == "science"
        result = resolve_filters([cond])
        assert result == [{"with": [{"metadata": {"field": "category", "equalTo": "science"}}]}]

    def test_bare_modality_auto_wraps(self):
        cond = ModalityCondition.text()
        result = resolve_filters([cond])
        assert result == [{"with": [{"modality": "text"}]}]
