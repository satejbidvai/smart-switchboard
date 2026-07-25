#!/usr/bin/env python3
"""Control Tuya smart bulbs over the local network."""

import json
import sys
from pathlib import Path

import tinytuya

DEVICES_FILE = Path(__file__).parent / "devices.json"
COMMANDS = ("toggle", "on", "off", "warm", "color")


def load_devices():
    """Load all devices from devices.json."""
    with open(DEVICES_FILE) as f:
        devices = json.load(f)

    # Support both flat list and wrapped {"devices": [...]} format
    if isinstance(devices, dict):
        devices = devices.get("devices", [])

    return devices


def load_device(name=None):
    """Load a device from devices.json by name. If name is None and only one device exists, use it."""
    devices = load_devices()

    if not devices:
        return None

    if name:
        match = next((d for d in devices if d.get("name", "").lower() == name.lower()), None)
        return match

    if len(devices) == 1:
        return devices[0]

    # Multiple devices: default to the first bulb
    bulb = next((d for d in devices if d.get("category") == "dj"), None)
    return bulb


def connect(device_info):
    """Create a tinytuya Device connection from device config."""
    category = device_info.get("category", "")
    kwargs = dict(
        dev_id=device_info["id"],
        address=device_info.get("ip", "Auto"),
        local_key=device_info["key"],
        version=float(device_info.get("version", 3.3)),
    )
    if category == "cz":
        device = tinytuya.OutletDevice(**kwargs)
    else:
        device = tinytuya.BulbDevice(**kwargs)
    # status() triggers device-type auto-detection
    device.status()
    return device


def run(command, device_name=None):
    # "off" with no device name → turn off ALL devices
    if command == "off" and not device_name:
        for info in load_devices():
            try:
                device = connect(info)
                device.turn_off()
            except Exception:
                pass
        return

    device_info = load_device(device_name)
    if not device_info:
        return

    device = connect(device_info)

    if command == "on":
        device.turn_on()
    elif command == "off":
        device.turn_off()
    elif command == "toggle":
        state = device.state()
        is_on = state.get("is_on")
        if is_on is None:
            # Fallback: read raw DPs (cached from connect())
            dps = device.status().get("dps", {})
            is_on = dps.get("20", dps.get("1", False))
        if is_on:
            device.turn_off()
        else:
            device.turn_on()
    elif command == "warm":
        device.turn_on()
        device.set_mode("white")
    elif command == "color":
        device.turn_on()
        device.set_mode("colour")


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
