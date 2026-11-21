"""Checks ka saancha, registry, config aur namoona check."""

import asyncio
from pathlib import Path

import pytest

from mailonix.checks import ALL_CHECKS, Check, CheckConfigError, load_checks
from mailonix.checks.header_auth import HeaderAuthCheck
from mailonix.checks.testing import BrokenCheck, SlowCheck
from mailonix.config import Settings
from mailonix.contracts import Signal, SignalStatus

REPO_CONFIG = Path("config/checks.toml")


def settings(**kw) -> Settings:
    kw.setdefault("checks_config", REPO_CONFIG)
    return Settings(_env_file=None, **kw)


# ---- registry ----

def test_registry_has_the_six_decided_checks():
    assert [c.name for c in ALL_CHECKS] == [
        "header_auth", "threat_intel", "links", "attachments", "behaviour", "intent"]
    assert [c.group for c in ALL_CHECKS] == ["A", "B", "C", "D", "E", "F"]


def test_test_only_checks_are_not_registered():
    names = {c.name for c in ALL_CHECKS}
    assert "broken_check" not in names and "slow_check" not in names


def test_load_all_by_default():
    loaded = load_checks(settings())
    assert loaded.names == tuple(c.name for c in ALL_CHECKS)
    assert loaded.disabled == ()


def test_disable_from_env(monkeypatch):
    monkeypatch.setenv("DISABLED_CHECKS", "intent, links")
    loaded = load_checks(settings())
    assert "intent" not in loaded.names and "links" not in loaded.names
    assert loaded.disabled == ("intent", "links")


def test_unknown_disabled_name_is_an_error():
    with pytest.raises(CheckConfigError, match="anjaan"):
        load_checks(settings(disabled_checks="intnet"))


def test_bad_class_rejected():
    class Bad(Check):
        name = "Bad Name"
        group = "Z"

        async def run(self, email):  # pragma: no cover
            ...

    with pytest.raises(TypeError):
        load_checks(settings(), classes=(Bad,))


# ---- config/checks.toml ----

def test_toml_value_overrides_default(tmp_path):
    cfg = tmp_path / "checks.toml"
    cfg.write_text("[header_auth]\nreply_to_mismatch_value = 0.9\n")
    loaded = load_checks(settings(checks_config=cfg))
    header = next(c for c in loaded.checks if c.name == "header_auth")
    assert header.params["reply_to_mismatch_value"] == 0.9


def test_toml_typo_in_setting_is_an_error(tmp_path):
    cfg = tmp_path / "checks.toml"
    cfg.write_text("[header_auth]\nreply_to_mismatch_valu = 0.9\n")
    with pytest.raises(CheckConfigError, match="anjaan setting"):
        load_checks(settings(checks_config=cfg))


def test_toml_unknown_check_is_an_error(tmp_path):
    cfg = tmp_path / "checks.toml"
    cfg.write_text("[header_auht]\nx = 1\n")
    with pytest.raises(CheckConfigError, match="anjaan checks"):
        load_checks(settings(checks_config=cfg))


def test_missing_config_file_is_an_error(tmp_path):
    with pytest.raises(CheckConfigError, match="nahi mili"):
        load_checks(settings(checks_config=tmp_path / "nahi.toml"))


def test_fingerprint_changes_with_values_and_disabled(tmp_path):
    base = load_checks(settings()).fingerprint
    cfg = tmp_path / "checks.toml"
    cfg.write_text("[header_auth]\nreply_to_mismatch_value = 0.9\n")
    assert load_checks(settings(checks_config=cfg)).fingerprint != base
    assert load_checks(settings(disabled_checks="intent")).fingerprint != base
    assert load_checks(settings()).fingerprint == base  # wohi settings = wohi fingerprint


# ---- har check ka output ----

async def test_every_check_returns_valid_signal(make_email):
    for check in load_checks(settings()).checks:
        sig = await check.run(make_email())
        assert isinstance(sig, Signal)
        assert sig.module == check.name


async def test_placeholders_abstain_never_safe(make_email):
    for check in load_checks(settings()).checks:
        if check.name == "header_auth":
            continue
        sig = await check.run(make_email())
        assert sig.status is SignalStatus.ABSTAINED
        assert sig.value is None
        assert sig.reasons[0].code == "not_implemented"


# ---- header_auth (namoona check) ----

async def test_header_auth_no_reply_to(make_email):
    sig = await HeaderAuthCheck().run(make_email(reply_to=None))
    assert sig.status is SignalStatus.OK and sig.value == 0.0 and sig.reasons == ()


async def test_header_auth_same_domain(make_email):
    sig = await HeaderAuthCheck().run(make_email(reply_to="Accounts@SSUET-lab.test"))
    assert sig.value == 0.0


async def test_header_auth_mismatch(make_email):
    sig = await HeaderAuthCheck().run(make_email(reply_to="ceo.private@freemail.test"))
    assert sig.status is SignalStatus.OK
    assert sig.value == 0.6
    assert sig.reasons[0].code == "reply_to_mismatch"
    assert sig.details == {"from_domain": "ssuet-lab.test", "reply_to_domain": "freemail.test"}


async def test_header_auth_value_comes_from_params(make_email):
    sig = await HeaderAuthCheck({"reply_to_mismatch_value": 0.3}).run(make_email(reply_to="x@other.test"))
    assert sig.value == 0.3


async def test_header_auth_no_from_abstains(make_email):
    sig = await HeaderAuthCheck().run(make_email(from_addr=None))
    assert sig.status is SignalStatus.ABSTAINED
    assert sig.reasons[0].code == "no_from_address"


# ---- test-only checks (G1.3 orchestrator ke liye) ----

async def test_broken_check_raises(make_email):
    with pytest.raises(RuntimeError):
        await BrokenCheck().run(make_email())


async def test_slow_check_is_slow(make_email):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(SlowCheck({"sleep_seconds": 5}).run(make_email()), timeout=0.05)
