from enum import Enum

import pytest


CUSTOM_SECRET = "0123456789abcdefghijklmnopqrstuvwxyz"


def test_master_secret(mocker):
    from derex.runner.secrets import get_master_secret

    secret = get_master_secret()
    assert secret


def test_master_secret_default_filename(mocker):
    """If a file exists on the default path it should be taken into consideration.
    Also make sure file contents are stripped from whitespace.
    """
    from derex.runner.secrets import get_master_secret

    mocker.patch("derex.runner.secrets.os.access", return_value=True)
    mocker.patch(
        "derex.runner.secrets.Path.read_text", return_value=CUSTOM_SECRET + "\n"
    )
    assert get_master_secret() == CUSTOM_SECRET


def test_master_secret_default_filename_not_readable(mocker):
    """If the file exists but is not readable we should log an error.
    """
    from derex.runner.secrets import get_master_secret

    mocker.patch("derex.runner.secrets.os.access", return_value=False)
    mocker.patch("derex.runner.secrets.Path.exists", return_value=True)
    logger = mocker.patch("derex.runner.secrets.logger")

    assert get_master_secret()
    logger.error.assert_called_once()


def test_master_secret_custom_filename(tmp_path, monkeypatch):
    """If the file exists but is not readable we should log an error.
    If the file contains a bad secret (too short, too long or not enough entropy)
    an exception is raised.
    """
    from derex.runner.secrets import get_master_secret
    from derex.runner.secrets import DerexSecretError

    secret_path = tmp_path / "main_secret"
    secret_path.write_text("\n" + CUSTOM_SECRET + "\n")
    monkeypatch.setenv("DEREX_MAIN_SECRET_PATH", str(secret_path))
    assert get_master_secret() == CUSTOM_SECRET

    secret_path.write_text("a" * 5000)
    with pytest.raises(DerexSecretError):
        get_master_secret()  # Too long

    secret_path.write_text("a")
    with pytest.raises(DerexSecretError):
        get_master_secret()  # Too short

    secret_path.write_text("a" * 20)
    with pytest.raises(DerexSecretError):
        get_master_secret()  # Not enough entropy


def test_derived_secret():
    from derex.runner.secrets import get_secret
    from derex.runner.secrets import compute_entropy

    class FooSecrets(Enum):
        foo = "foo"
        bar = "bar"

    foo_secret = get_secret(FooSecrets.foo)
    # The same name should always yield the same secrets
    assert get_secret(FooSecrets.foo) == foo_secret

    # Two names should have different secrets
    assert foo_secret != get_secret(FooSecrets.bar)

    # Secrets must have enough entropy
    assert compute_entropy(foo_secret) > 256
