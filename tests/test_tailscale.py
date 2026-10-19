import json
import subprocess

import pytest

from secondhands.api import tailscale

STATUS = {
    "BackendState": "Running",
    "CurrentTailnet": {"Name": "owner@example.com", "MagicDNSSuffix": "tail0.ts.net"},
    "Health": [],
    "Self": {
        "HostName": "PC",
        "DNSName": "pc.tail0.ts.net.",
        "OS": "windows",
        "UserID": 1,
        "TailscaleIPs": ["100.0.0.1", "fd7a::1"],
    },
    "Peer": {
        "a": {
            "HostName": "localhost",
            "DNSName": "phone.tail0.ts.net.",
            "OS": "iOS",
            "UserID": 1,
            "TailscaleIPs": ["100.0.0.2"],
            "Online": False,
        },
        "b": {
            "HostName": "device-of-shared-to-user",
            "DNSName": "",
            "UserID": 2,
            "TailscaleIPs": ["100.0.0.3"],
            "Online": True,
            "ShareeNode": True,
        },
        "c": {
            "HostName": "mac",
            "DNSName": "mac.tail0.ts.net.",
            "OS": "macOS",
            "UserID": 1,
            "TailscaleIPs": ["100.0.0.4"],
            "Online": True,
        },
    },
    "User": {
        "1": {"LoginName": "owner@example.com", "DisplayName": "Owner"},
        "2": {"LoginName": "mate@example.com", "DisplayName": "Teammate"},
    },
}


def fake_run(pings):
    def run(*args, timeout):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 0, json.dumps(STATUS), "")
        ip = args[-1]
        if ip in pings:
            return subprocess.CompletedProcess(
                args, 0, f"pong from x ({ip}) via DERP(sfo) in 9ms\n", ""
            )
        return subprocess.CompletedProcess(args, 1, "", "no reply")

    return run


def test_status_hides_login_names_and_lists_people(monkeypatch):
    monkeypatch.setattr(tailscale, "_run", fake_run(set()))
    summary = tailscale.status()
    assert "example.com" not in json.dumps(summary)
    assert summary["state"] == "Running" and summary["tailnet"] == "tail0.ts.net"
    assert summary["self"]["ip"] == "100.0.0.1" and summary["self"]["online"]
    assert [d["hostname"] for d in summary["devices"]] == [
        "device-of-shared-to-user",
        "mac",
        "phone",
    ]
    assert summary["people"] == [
        {"name": "Owner", "access": "member", "online": True},
        {"name": "Teammate", "access": "shared", "online": True},
    ]


def test_missing_cli_reports_not_installed(monkeypatch):
    def missing(*args, timeout):
        raise FileNotFoundError("tailscale")

    monkeypatch.setattr(tailscale, "_run", missing)
    assert tailscale.status() == {
        "installed": False,
        "state": "NotInstalled",
        "self": None,
        "devices": [],
        "people": [],
    }


def test_check_skips_offline_and_sharee_devices(monkeypatch):
    monkeypatch.setattr(tailscale, "_run", fake_run({"100.0.0.4"}))
    probed = []
    monkeypatch.setattr(
        tailscale,
        "_ssh_port",
        lambda ip: probed.append(ip) or {"ok": ip == "100.0.0.1", "detail": ""},
    )
    summary = tailscale.check()
    devices = {d["hostname"]: d for d in summary["devices"]}
    assert summary["self"]["check"]["ssh"]["ok"]
    assert devices["mac"]["check"]["ping"] == {"ok": True, "detail": "via DERP(sfo) in 9ms"}
    assert "check" not in devices["phone"] and "check" not in devices["device-of-shared-to-user"]
    assert sorted(probed) == ["100.0.0.1", "100.0.0.4"]


def test_api_routes(monkeypatch):
    pytest.importorskip("fastapi", reason="Install the dashboard extra for API tests")
    from fastapi.testclient import TestClient

    from secondhands.api.app import create_app

    monkeypatch.setattr(tailscale, "_run", fake_run(set()))
    monkeypatch.setattr(tailscale, "_ssh_port", lambda ip: {"ok": False, "detail": ""})
    with TestClient(create_app()) as client:
        assert client.get("/api/tailscale").json()["state"] == "Running"
        assert client.post("/api/tailscale/check").json()["self"]["check"]["ssh"]["ok"] is False
