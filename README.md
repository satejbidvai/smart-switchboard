# Smart Switchboard

Control Tuya smart devices from your Mac over the local network. No cloud, no Smart Life app, no global installs. One keyboard shortcut, sub-second response.

## Why this exists

The Smart Life app cannot be installed on macOS (Tuya blocks Apple Silicon Mac availability). The Continuity widget relays through your iPhone, which relays through Tuya's cloud, which is slow and fragile. Apple Shortcuts fail on Mac because the action provider (Smart Life) isn't there.

This project bypasses all of that. It talks directly to the bulb over your home Wi-Fi using TCP port 6668, encrypted with the device's `local_key`. No cloud round-trip at runtime.

## How it works

```
Mac (switch.py) --TCP 6668--> Bulb (on your LAN)
```

Every Tuya device has a `local_key` that encrypts LAN communication. This key lives in Tuya's cloud, not in the Smart Life app. You extract it once using the tinytuya wizard, then never need the cloud again.

"Wipro" is a brand label. The bulb is a Tuya device. Smart Life is Tuya's white-label app. This project works with any Tuya-protocol device.

## Prerequisites

- Python 3 (ships with macOS)
- A Tuya IoT developer account at [iot.tuya.com](https://iot.tuya.com)
- Your bulb paired in the Smart Life app and connected to your Wi-Fi

## One-time setup

### 1. Create the Tuya IoT cloud project

This is only for extracting the `local_key`. The cloud is not used at runtime.

1. Log in to [iot.tuya.com](https://iot.tuya.com)
2. Create a Cloud project: Development Method = **Smart Home**, Data Center = **India** (match your Smart Life account region)
3. Under **Service API**, subscribe to: **IoT Core**, **Authorization**, **Smart Home Basic Service**, **Smart Home Scene Linkage**
4. Link your Smart Life account: project **Devices** tab > **Link App Account** > **Tuya App Account Authorization** > scan the QR with Smart Life (Me > scan icon)
5. Your devices should now appear in the project's device list

### 2. Install dependencies

```bash
cd ~/Work/Personal/smart-switchboard
python3 -m venv .venv
.venv/bin/pip install tinytuya
```

### 3. Extract the local key

```bash
.venv/bin/python -m tinytuya wizard
```

It prompts for:
- **API Key** = Access ID from the project Overview page
- **API Secret** = Access Secret from the project Overview page
- **Device ID** = any device ID from the project's device list
- **Region** = `in` (India). This must match your Smart Life account region. Wrong region = silent failure.

Say **Y** to "Download DP Name mappings".

This writes `devices.json` with each device's `name`, `id`, `key` (the local key), and DP mapping.

### 4. Scan for IP and protocol version

Your Mac must be on the **same Wi-Fi** as the bulb (2.4 GHz).

```bash
.venv/bin/python -m tinytuya scan
```

Note the **IP** and **Version** from the output. Add both to `devices.json` manually:

```json
{
  "ip": "192.168.x.x",
  "version": "3.5"
}
```

### 5. Verify it works

```bash
.venv/bin/python switch.py on
.venv/bin/python switch.py off
```

## Commands

```bash
.venv/bin/python switch.py <command> [device_name]
```

| Command | Effect |
|---|---|
| `toggle` | Flip power on/off |
| `on` | Turn on |
| `off` | Turn off |
| `warm` | Turn on in warm white mode |
| `color` | Turn on in color mode |

`device_name` is optional. When omitted:
- `off` turns off **all** devices
- All other commands default to the first bulb

To target a specific device, pass its name (case-insensitive match):

```bash
.venv/bin/python switch.py toggle "Room Bulb"
.venv/bin/python switch.py off "10Amp Smart Plug"
```

## Apple Shortcuts

Create one Shortcut per command using the **Run Shell Script** action.

1. Open the **Shortcuts** app
2. Create a new shortcut, name it (e.g. "Toggle Light")
3. Add the **Run Shell Script** action
4. Paste the full command:
   ```
   /Users/satejbidvai/Work/Personal/smart-switchboard/.venv/bin/python /Users/satejbidvai/Work/Personal/smart-switchboard/switch.py toggle
   ```
5. To bind a keyboard shortcut: click the shortcut settings (top right) > **Add Keyboard Shortcut** > press your key combo

Full paths are required because Shortcuts don't load your shell profile.

These shortcuts also appear in Raycast automatically.

## Adding a new device

1. Pair the device in the Smart Life app
2. Re-run the wizard to pull its `local_key`:
   ```bash
   .venv/bin/python -m tinytuya wizard
   ```
3. Scan for its IP:
   ```bash
   .venv/bin/python -m tinytuya scan
   ```
4. Add `ip` and `version` to its entry in `devices.json`
5. Control it by name:
   ```bash
   .venv/bin/python switch.py toggle "New Device Name"
   ```

## When to re-run what

| Situation | What to re-run |
|---|---|
| Bulb's IP changed (router reboot, DHCP lease expired) | `tinytuya scan`, then update `ip` in `devices.json` |
| Bulb was factory-reset or re-paired in Smart Life | `tinytuya wizard` (the `local_key` rotates on reset) |
| Added a new device to Smart Life | `tinytuya wizard` then `tinytuya scan` |
| Tuya IoT trial expired (after ~6 months) | Only affects the wizard. Local control keeps working with the existing key. Renew at iot.tuya.com: Cloud > Cloud Services > IoT Core > Extend Trial Period. |
| Moved to a new router / network | `tinytuya scan` for new IPs. Set DHCP reservations to avoid this. |

Tip: set a **DHCP reservation** on your router for the bulb's MAC address. This makes the IP permanent and eliminates the most common reason to re-run anything.

## Troubleshooting

**`permission deny` (code 28841001) during wizard** — Your Tuya IoT project is missing API subscriptions. Go to the project's Service API section and subscribe to IoT Core, Authorization, Smart Home Basic Service, and Smart Home Scene Linkage. Disable your popup blocker while subscribing.

**Wizard returns no devices** — Wrong data center. Your Smart Life account region must match the cloud project's data center. Check your region in Smart Life: Me > Settings > Account and Security > Region. India = data center India, region code `in`.

**Scan finds nothing** — Mac isn't on the same Wi-Fi as the bulb, or a firewall is blocking UDP 6666/6667/7000 and TCP 6668. Bulbs use 2.4 GHz; if your Mac is on a separate 5 GHz SSID, the scan won't find it.

**Commands silently fail** — The bulb is powered off at the wall switch, the IP changed, or the `local_key` rotated. Check power, re-scan, and re-run the wizard in that order.

## Uninstall

Delete the project folder. Nothing was installed globally.

```bash
rm -rf ~/Work/Personal/smart-switchboard
```

Remove any Apple Shortcuts you created manually.

## References

- [tinytuya](https://github.com/jasonacox/tinytuya) — Python library for local Tuya device control
- [Tuya IoT Platform Configuration Guide](https://github.com/tuya/tuya-home-assistant/wiki/Tuya-IoT-Platform-Configuration-Guide)
- [Data Center / Region Mapping](https://developer.tuya.com/en/docs/iot/oem-app-data-center-distributed?id=Kafi0ku9l07qb)
