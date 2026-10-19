"""Read-only Tailscale reachability checks for the team's remote-access setup."""

import json
import shutil
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor

SSH_PORT = 22


def _run(*args, timeout):
    executable = shutil.which("tailscale")
    if not executable:
        raise FileNotFoundError("tailscale")
    return subprocess.run(
        [executable, *args], capture_output=True, text=True, timeout=timeout, check=False
    )


def _device(node, users):
    # Login names are email addresses; return only the display name to the local page.
    owner = users.get(str(node.get("UserID")), {}).get("DisplayName", "")
    ips = node.get("TailscaleIPs") or []
    dns_name = node.get("DNSName", "").rstrip(".")
    # Mobile clients report "localhost"; the MagicDNS label is the name people recognise.
    hostname = dns_name.split(".")[0] if dns_name else node.get("HostName", "")
    return {
        "hostname": hostname,
        "dns_name": dns_name,
        "ip": next((ip for ip in ips if "." in ip), ips[0] if ips else ""),
        "os": node.get("OS", ""),
        "owner": owner,
        "online": bool(node.get("Online")),
        # A sharee is a teammate's device this machine was shared to: it can connect in,
        # but this machine cannot reach it, so it is listed and not tested.
        "sharee": bool(node.get("ShareeNode")),
        "last_seen": node.get("LastSeen", ""),
    }


def status():
    """Summarise `tailscale status --json` without login names or keys."""
    try:
        result = _run("status", "--json", timeout=5)
    except FileNotFoundError:
        return {
            "installed": False,
            "state": "NotInstalled",
            "self": None,
            "devices": [],
            "people": [],
        }
    except subprocess.TimeoutExpired:
        return {"installed": True, "state": "Timeout", "self": None, "devices": [], "people": []}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"installed": True, "state": "Unreadable", "self": None, "devices": [], "people": []}
    users = data.get("User") or {}
    me = _device(data["Self"], users) if data.get("Self") else None
    if me:
        me["online"] = data.get("BackendState") == "Running"
    devices = sorted(
        (_device(node, users) for node in (data.get("Peer") or {}).values()),
        key=lambda d: (not d["online"], d["hostname"].lower()),
    )
    people = {}
    for device in [me, *devices]:
        if device and device["owner"]:
            person = people.setdefault(
                device["owner"],
                {
                    "name": device["owner"],
                    "access": "shared" if device["sharee"] else "member",
                    "online": False,
                },
            )
            person["online"] |= device["online"]
    return {
        "installed": True,
        "state": data.get("BackendState", "Unknown"),
        "tailnet": (data.get("CurrentTailnet") or {}).get("MagicDNSSuffix", ""),
        "health": data.get("Health") or [],
        "self": me,
        "devices": devices,
        "people": list(people.values()),
    }


def _ping(ip):
    try:
        result = _run("ping", "-c", "1", "--timeout", "3s", ip, timeout=6)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"ok": False, "detail": "no reply"}
    line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if result.returncode == 0 and line.startswith("pong"):
        # e.g. "pong from host (100.x) via DERP(sfo) in 80ms" or "via 1.2.3.4:41641 in 30ms"
        return {"ok": True, "detail": line.split(") ", 1)[-1]}
    return {"ok": False, "detail": "no reply"}


def _ssh_port(ip):
    try:
        with socket.create_connection((ip, SSH_PORT), timeout=3):
            return {"ok": True, "detail": f"port {SSH_PORT} open"}
    except OSError:
        return {"ok": False, "detail": f"port {SSH_PORT} closed or filtered"}


def check():
    """Ping each reachable device over the tailnet and test whether it accepts SSH."""
    summary = status()
    me = summary["self"]
    if me and me["ip"]:
        me["check"] = {
            "ping": {"ok": me["online"], "detail": "this device"},
            "ssh": _ssh_port(me["ip"]),
        }
    targets = [d for d in summary["devices"] if d["online"] and not d["sharee"] and d["ip"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        pings = list(pool.map(_ping, [d["ip"] for d in targets]))
        ports = list(pool.map(_ssh_port, [d["ip"] for d in targets]))
    for device, ping, port in zip(targets, pings, ports, strict=True):
        device["check"] = {"ping": ping, "ssh": port}
    return summary
