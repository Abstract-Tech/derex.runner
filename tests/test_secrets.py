from derex.runner.project import Project
from enum import Enum
from importlib import reload

import pytest


CUSTOM_SECRET = "0123456789abcdefghijklmnopqrstuvwxyz"


def test_unreadable_main_secret(mocker, minimal_project):
    with minimal_project:
        project = Project()

        mocker.patch("derex.runner.secrets.os.access", return_value=False)
        assert project.main_secret == "Default secret"


def test_main_secret_default_filename(mocker, minimal_project):
    """If a file exists on the default path it should be taken into consideration.
    Also make sure file contents are stripped from whitespace.
    """
    with minimal_project:
        project = Project()

        mocker.patch("derex.runner.secrets.os.access", return_value=True)
        mocker.patch(
            "derex.runner.project.Path.read_text", return_value=CUSTOM_SECRET + "\n"
        )
        assert project.main_secret == CUSTOM_SECRET


def test_main_secret_default_filename_not_readable(mocker, minimal_project):
    """If the file exists but is not readable we should log an error."""
    with minimal_project:
        project = Project()
        environment = project.environment

        mocker.patch("derex.runner.secrets.os.access", return_value=False)
        mocker.patch("derex.runner.project.Path.exists", return_value=True)
        logger = mocker.patch("derex.runner.project.logger")

        # Since we are patching derex.runner.project.Path.exists we can't call
        # project.main_secret since that will fail when checking the existence of a
        # project environment file
        assert project.get_main_secret(environment) is None
        logger.error.assert_called_once()


def test_main_secret_custom_filename(tmp_path, monkeypatch, minimal_project):
    """If the file exists but is not readable we should log an error.
    If the file contains a bad secret (too short, too long or not enough entropy)
    an exception is raised.
    """
    from derex.runner.exceptions import DerexSecretError

    with minimal_project:
        project = Project()

        secret_path = tmp_path / "main_secret"
        secret_path.write_text("\n" + CUSTOM_SECRET + "\n")
        monkeypatch.setenv("DEREX_MAIN_SECRET_PATH", str(secret_path))
        assert project.main_secret == CUSTOM_SECRET

        secret_path.write_text("a" * 5000)
        with pytest.raises(DerexSecretError):
            project.main_secret  # Too long

        secret_path.write_text("a")
        with pytest.raises(DerexSecretError):
            project.main_secret  # Too short

        secret_path.write_text("a" * 20)
        with pytest.raises(DerexSecretError):
            project.main_secret  # Not enough entropy


def test_derived_secret(minimal_project):
    from derex.runner.secrets import compute_entropy

    with minimal_project:
        project = Project()

        foo_secret = project.get_secret(FooSecrets.foo)
        # The same name should always yield the same secrets
        assert project.get_secret(FooSecrets.foo) == foo_secret

        # Two names should have different secrets
        assert foo_secret != project.get_secret(FooSecrets.bar)

        # Secrets must have enough entropy
        assert compute_entropy(foo_secret) > 256


def test_derived_secret_no_scrypt_available(no_scrypt, minimal_project):
    with minimal_project:
        import derex.runner.project

        project = derex.runner.project.Project()

        reload(derex.runner.secrets)
        reload(derex.runner.project)

        project.get_secret(FooSecrets.foo)


try:
    from hashlib import scrypt
    from scrypt import scrypt  # type:ignore  # noqa

    only_one_scrypt_implementations = False
except ImportError:
    only_one_scrypt_implementations = True


@pytest.mark.skipif(
    only_one_scrypt_implementations, reason="We don't have both openssl>=1.1 and scrypt"
)
def test_derived_secret_no_scrypt_same_result_as_with_scrypt():
    from derex.runner.secrets import scrypt_hash_addon
    from derex.runner.secrets import scrypt_hash_stdlib

    TEST_CASES = [("aaa", "bbb"), ("The master secret", "the service")]
    for a, b in TEST_CASES:
        assert scrypt_hash_addon(a, b) == scrypt_hash_stdlib(a, b)


@pytest.fixture
def no_scrypt():
    import hashlib

    original_scrypt = hashlib.scrypt
    del hashlib.scrypt
    yield
    hashlib.scrypt = original_scrypt


class FooSecrets(Enum):
    foo = "foo"
    bar = "bar"
