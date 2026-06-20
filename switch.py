#!/usr/bin/env python3
"""Control Tuya smart bulbs over the local network."""

import json
import sys
from pathlib import Path

import tinytuya

DEVICES_FILE = Path(__file__).parent / "devices.json"
COMMANDS = ("toggle", "on", "off", "warm", "color")


def load_device(name=None):
    """Load a device from devices.json by name. If name is None and only one device exists, use it."""
    with open(DEVICES_FILE) as f:
        devices = json.load(f)

    # Support both flat list and wrapped {"devices": [...]} format
    if isinstance(devices, dict):
        devices = devices.get("devices", [])

    if not devices:
        return None

    if name:
        match = next((d for d in devices if d.get("name", "").lower() == name.lower()), None)
        return match

    if len(devices) == 1:
        return devices[0]

    return None


def connect(device_info):
    """Create a BulbDevice connection from device config."""
    bulb = tinytuya.BulbDevice(
        dev_id=device_info["id"],
        address=device_info.get("ip", "Auto"),
        local_key=device_info["key"],
        version=float(device_info.get("version", 3.3)),
    )
    # status() triggers bulb-type auto-detection (A/B/C)
    bulb.status()
    return bulb


def run(command, device_name=None):
    device_info = load_device(device_name)
    if not device_info:
        return

    bulb = connect(device_info)

    if command == "on":
        bulb.turn_on()
    elif command == "off":
        bulb.turn_off()
    elif command == "toggle":
        state = bulb.state()
        is_on = state.get("is_on")
        if is_on is None:
            # Fallback: read raw DPs
            dps = bulb.status().get("dps", {})
            is_on = dps.get("20", dps.get("1", False))
        if is_on:
            bulb.turn_off()
        else:
            bulb.turn_on()
    elif command == "warm":
        bulb.turn_on()
        bulb.set_mode("white")
    elif command == "color":
        bulb.turn_on()
        bulb.set_mode("colour")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        return

    command = sys.argv[1]
    device_name = sys.argv[2] if len(sys.argv) > 2 else None
    run(command, device_name)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
