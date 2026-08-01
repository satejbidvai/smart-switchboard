#!/usr/bin/env python3
"""Scan the LAN for Tuya devices, then update IPs in devices.json."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DEVICES_FILE = ROOT / "devices.json"
SNAPSHOT_FILE = ROOT / "snapshot.json"


def scan():
    """Run tinytuya scan to refresh snapshot.json."""
    print("Scanning LAN for devices...")
    result = subprocess.run(
        [sys.executable, "-m", "tinytuya", "scan"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Scan failed:\n{result.stderr.strip()}")
        sys.exit(1)
    print("Scan complete.")


def main():
    scan()

    with open(SNAPSHOT_FILE) as f:
        snapshot = json.load(f)
    snap_devices = snapshot.get("devices", [])

    # Build id → ip lookup from the scan snapshot
    snap_ips = {d["id"]: d["ip"] for d in snap_devices if "id" in d and "ip" in d}

    with open(DEVICES_FILE) as f:
        devices = json.load(f)

    updated = []
    for device in devices:
        dev_id = device.get("id")
        old_ip = device.get("ip")
        new_ip = snap_ips.get(dev_id)

        if new_ip and new_ip != old_ip:
            device["ip"] = new_ip
            updated.append((device.get("name", dev_id), old_ip, new_ip))

    if not updated:
        print("All IPs are already up to date.")
        return

    with open(DEVICES_FILE, "w") as f:
        json.dump(devices, f, indent=4)
        f.write("\n")

    for name, old, new in updated:
        print(f"{name}: {old} -> {new}")


if __name__ == "__main__":
    main()
