# AGENTS.md

Python + tinytuya project that controls Tuya smart devices over the local network (TCP 6668, encrypted with device `local_key`). Single entry point: `switch.py`. No build step, no tests, no linter.

## Commands

```bash
.venv/bin/python switch.py <toggle|on|off|warm|color|monitor> [device_name]
.venv/bin/python update_ips.py
```

Device name is optional. When omitted: `off` turns off **all** devices; `monitor` defaults to the smart plug; other commands default to the first bulb (category `dj`).

`update_ips.py` runs a LAN scan and updates changed IPs in `devices.json` automatically.

## Gitignored files that exist locally

These files are present on disk but invisible to git-based file searches. Never assume they are missing.

| File | Purpose |
|---|---|
| `devices.json` | Runtime config with device IDs, local keys, IPs, DP mappings. **Never overwrite without reading first.** |
| `snapshot.json` | Output of `tinytuya scan`. Contains current LAN device IPs. |
| `tinytuya.json` | Tuya cloud API credentials (only needed for wizard re-runs). |
| `tuya-raw.json` | Raw cloud API dump (wizard artifact). |
| `.venv/` | Python virtual environment. |

## Key relationship: snapshot.json vs devices.json

`tinytuya scan` writes discovered devices to `snapshot.json`. It does NOT update `devices.json`. When an IP changes, run `update_ips.py` — it scans the LAN and updates only the `ip` field in `devices.json`. Never replace `devices.json` wholesale. It contains extensive DP mappings and metadata that `snapshot.json` does not.

## Diagnosing "shortcut stopped working"

In order:

1. Is the bulb physically powered on (wall switch)?
2. Run `switch.py toggle` manually — does it work from the terminal?
3. If silent failure: run `.venv/bin/python update_ips.py` to scan and update IPs automatically.
4. If scan finds nothing: Mac is on a different network than the bulb (5 GHz vs 2.4 GHz).
5. If IP is correct but still fails: `local_key` rotated (factory reset or re-pair). Re-run `.venv/bin/python -m tinytuya wizard`.

## Adding a new device

1. Pair in Smart Life app
2. `.venv/bin/python -m tinytuya wizard` — pulls `local_key` for all linked devices
3. `.venv/bin/python -m tinytuya scan` — discovers LAN IPs
4. Add `ip` and `version` fields to the new device's entry in `devices.json`

## Non-obvious facts

- Tuya IoT cloud region is `in` (India). Wrong region in the wizard = zero devices returned, no error.
- The wizard populates `devices.json` with `name`, `id`, `key`, and DP mappings but NOT `ip` or `version`. Those must be added manually after running a scan.
- Apple Shortcuts don't load shell profiles. Commands must use absolute paths: `/Users/satejbidvai/Work/Personal/smart-switchboard/.venv/bin/python /Users/satejbidvai/Work/Personal/smart-switchboard/switch.py toggle`
- tinytuya uses British spelling: `set_mode('colour')`, not `set_mode('color')`. The CLI command is `color` but the API call is `colour`.
- Adding a new device to the network can cause existing devices to get new DHCP IPs — this is the most common reason the shortcut breaks.
- The smart plug (category `cz`) uses `OutletDevice` and DP `1` for switch control; the bulb (category `dj`) uses `BulbDevice` and DP `20`.
- The Tuya IoT Core trial expires every ~6 months. Renew at iot.tuya.com → Cloud → Cloud Services → IoT Core → Extend Trial Period. Only needed for wizard runs; local control is unaffected.

## Boundaries

- Never commit `devices.json`, `snapshot.json`, `tinytuya.json`, or `tuya-raw.json` — they contain device keys and cloud credentials.
- Never overwrite or recreate `devices.json` without reading its current contents. It is 480+ lines with DP mappings that cannot be regenerated from `snapshot.json` alone.
- Never expose device IDs, local keys, MAC addresses, or Tuya API credentials in commits or responses.
- This repo is Tuya-protocol only. No other ecosystems (Hue, Tapo, Matter).
