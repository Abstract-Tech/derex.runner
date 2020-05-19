import pytest


@pytest.mark.slowtest
def test_run_django_script(testproj):
    with testproj:
        from derex.runner.project import Project
        from derex.runner.compose_utils import run_django_script

        result = run_django_script(
            Project(), "import json; print(json.dumps(dict(foo='bar', one=1)))"
        )
        assert result == {"foo": "bar", "one": 1}

        result = run_django_script(
            Project(), "import json; print('This is not { the JSON you re looking for')"
        )
        assert result is None
