from enum import Enum
from importlib import reload

import pytest


CUSTOM_SECRET = "0123456789abcdefghijklmnopqrstuvwxyz"


def test_master_secret(mocker):
    from derex.runner.secrets import _get_master_secret

    mocker.patch("derex.runner.secrets.os.access", return_value=False)
    assert _get_master_secret() is None


def test_master_secret_default_filename(mocker):
    """If a file exists on the default path it should be taken into consideration.
    Also make sure file contents are stripped from whitespace.
    """
    from derex.runner.secrets import _get_master_secret

    mocker.patch("derex.runner.secrets.os.access", return_value=True)
    mocker.patch(
        "derex.runner.secrets.Path.read_text", return_value=CUSTOM_SECRET + "\n"
    )
    assert _get_master_secret() == CUSTOM_SECRET


def test_master_secret_default_filename_not_readable(mocker):
    """If the file exists but is not readable we should log an error.
    """
    from derex.runner.secrets import _get_master_secret

    mocker.patch("derex.runner.secrets.os.access", return_value=False)
    mocker.patch("derex.runner.secrets.Path.exists", return_value=True)
    logger = mocker.patch("derex.runner.secrets.logger")

    assert _get_master_secret() is None
    logger.error.assert_called_once()


def test_master_secret_custom_filename(tmp_path, monkeypatch):
    """If the file exists but is not readable we should log an error.
    If the file contains a bad secret (too short, too long or not enough entropy)
    an exception is raised.
    """
    from derex.runner.secrets import _get_master_secret
    from derex.runner.secrets import DerexSecretError

    secret_path = tmp_path / "main_secret"
    secret_path.write_text("\n" + CUSTOM_SECRET + "\n")
    monkeypatch.setenv("DEREX_MAIN_SECRET_PATH", str(secret_path))
    assert _get_master_secret() == CUSTOM_SECRET

    secret_path.write_text("a" * 5000)
    with pytest.raises(DerexSecretError):
        _get_master_secret()  # Too long

    secret_path.write_text("a")
    with pytest.raises(DerexSecretError):
        _get_master_secret()  # Too short

    secret_path.write_text("a" * 20)
    with pytest.raises(DerexSecretError):
        _get_master_secret()  # Not enough entropy


def test_derived_secret():
    from derex.runner.secrets import get_secret
    from derex.runner.secrets import compute_entropy

    foo_secret = get_secret(FooSecrets.foo)
    # The same name should always yield the same secrets
    assert get_secret(FooSecrets.foo) == foo_secret

    # Two names should have different secrets
    assert foo_secret != get_secret(FooSecrets.bar)

    # Secrets must have enough entropy
    assert compute_entropy(foo_secret) > 256


def test_derived_secret_no_scrypt_available(no_scrypt):
    import derex.runner.secrets

    reload(derex.runner.secrets)

    derex.runner.secrets.get_secret(FooSecrets.foo)


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
    from derex.runner.secrets import scrypt_hash_stdlib
    from derex.runner.secrets import scrypt_hash_addon

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
