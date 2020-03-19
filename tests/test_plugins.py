def test_registry_basic():
    from derex.runner.plugins import Registry

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
    assert registry["first"] == "I should be first"
