from derex.runner.plugins import Registry
from itertools import permutations

import logging
import pytest


def test_registry_exception():
    registry = Registry()
    registry.add("one", "one", "badlocation")

    with pytest.raises(ValueError):
        registry.add("one", "one", "badlocation")

    with pytest.raises(ValueError):
        registry.deregister("doesnotexist")


def test_registry_basic():
    registry = Registry()
    registry.add("last", "I should be last", "_end")
    registry.add("first", "I should be first", "_begin")
    registry.add(
        "in-between-1", "I should be the first in between first and last", ">first"
    )
    registry.add(
        "in-between-2", "I should be the second in between first and last", "<last"
    )

    assert registry["last"] == "I should be last"
    assert registry[-1] == "I should be last"
    assert registry["first"] == "I should be first"
    assert registry[0] == "I should be first"

    # Now move the last to the beginning, just to prove we can
    registry.add("last", "I should be last", "_begin")
    assert registry[0] == "I should be last"


def test_registry_add_list():
    # TODO: adding a third elemnt in between begin and end makes this not
    # work anymore. It's good enough for what we're using it (allowing users
    # to hint where they want their options) but can be greatly improved.
    to_add = [
        ("last", "I should be last", "_end"),
        ("first", "I should be first", "_begin"),
        ("in-between-1", "I should be the first in between first and last", ">first"),
        ("in-between-2", "I should be the second in between first and last", "<last"),
    ]

    for variant in permutations(to_add):
        registry = Registry()
        registry.add_list(variant)
        assert tuple(registry) == (
            "I should be first",
            "I should be the first in between first and last",
            "I should be the second in between first and last",
            "I should be last",
        )


def test_registry_add_list_impossible():
    to_add = [
        ("zero", "zero", "_begin"),
        ("one", "one", "<two"),
        ("two", "two", "<one"),
    ]

    registry = Registry()
    with pytest.raises(ValueError):
        registry.add_list(to_add)


def test_plugin_sorting_and_validation(caplog):
    from derex.runner.plugins import sort_and_validate_plugins

    caplog.set_level(logging.DEBUG)
    plugins = [
        {"name": "missing-priority", "options": ["no", "priority"]},
        {"priority": "<missing-name", "options": ["no", "name"]},
        {"name": "missing-options", "priority": ">missing-options"},
        {
            "name": "valid-with-options",
            "priority": "_begin",
            "options": ["this", "list", "should", "contain"],
        },
        {
            "name": "valid-with-options-and-priority",
            "priority": ">valid-with-options",
            "options": ["only", "valid"],
        },
        {
            "name": "valid-with-empty-options",
            "priority": "_end",
            "options": ["plugins"],
        },
        {
            "name": "invalid-options-type",
            "priority": "<valid-with-empty-options",
            "options": "not a valid plugin",
        },
    ]

    plugins = sort_and_validate_plugins(plugins)

    assert caplog.text.count("Missing 'priority' field.") == 1
    assert caplog.text.count("Missing value for 'priority' field") == 1
    assert caplog.text.count("Missing 'name' field.") == 1
    assert caplog.text.count("Missing value for 'name' field") == 1
    assert caplog.text.count("Missing 'options' field.") == 1
    assert caplog.text.count("Plugins 'options' field must be a list.") == 2

    assert plugins == ["this", "list", "should", "contain", "only", "valid", "plugins"]
