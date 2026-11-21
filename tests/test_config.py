import pytest
from pydantic import ValidationError

from mailonix.config import Settings


def test_defaults_without_env_file():
    s = Settings(_env_file=None)
    assert s.ti_mode == "mock"
    assert s.delivery == "mailpit"
    assert s.scan_timeout_seconds == 10.0
    assert s.lab_trust_xclient is False


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TI_MODE", "hybrid")
    monkeypatch.setenv("SCAN_TIMEOUT_SECONDS", "4.5")
    s = Settings(_env_file=None)
    assert s.ti_mode == "hybrid"
    assert s.scan_timeout_seconds == 4.5


def test_bad_ti_mode_rejected(monkeypatch):
    monkeypatch.setenv("TI_MODE", "online")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
