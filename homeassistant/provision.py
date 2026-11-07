#!/usr/bin/env python3
"""Register the Audio Control dashboard in /config/configuration.yaml.

Runs on every start, before Home Assistant. Append-only and idempotent:

- No configuration.yaml yet (first boot): write Home Assistant's own default
  config first -- the same files HA would create -- so the dashboard exists
  from the very first start instead of after a restart.
- Marker present: already done, nothing to do.
- A top-level `lovelace:` block already exists: leave the file alone (two
  `lovelace:` keys would make HA reject the whole file) and print what to add.
- Otherwise: back up once, then append the block.

Never removes or rewrites anything the user wrote.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

CONFIG_DIR = Path("/config")
CONFIG = CONFIG_DIR / "configuration.yaml"
MARKER = "# --- audio_control dashboard (added by the balena template) ---"
BLOCK = f"""
{MARKER}
lovelace:
  dashboards:
    audio-control:
      mode: yaml
      title: Audio Control
      icon: mdi:speaker-multiple
      show_in_sidebar: true
      filename: dashboards/audio_control.yaml
"""


def has_top_level_key(text: str, key: str) -> bool:
    return any(
        line.startswith(f"{key}:") for line in text.splitlines() if line[:1] not in " \t#"
    )


def write_ha_defaults() -> bool:
    try:
        from homeassistant import config as ha_config
    except ImportError:
        return False
    writer = getattr(ha_config, "_write_default_config", None)
    return bool(writer and writer(str(CONFIG_DIR)))


def main() -> int:
    if not CONFIG.exists():
        if not write_ha_defaults():
            print("[haac] no configuration.yaml yet; dashboard is added on the next start")
            return 0
        print("[haac] wrote Home Assistant's default configuration")

    text = CONFIG.read_text(encoding="utf-8")
    if MARKER in text:
        return 0
    if has_top_level_key(text, "lovelace"):
        print(
            "[haac] configuration.yaml already has a 'lovelace:' block; not changing it."
            " To add the Audio Control dashboard, put this under it:" + BLOCK.split("lovelace:", 1)[1]
        )
        return 0

    backup = CONFIG.with_suffix(".yaml.pre-audio-control")
    if not backup.exists():
        shutil.copy2(CONFIG, backup)
    CONFIG.write_text(text.rstrip("\n") + "\n" + BLOCK, encoding="utf-8")
    print("[haac] registered the Audio Control dashboard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
