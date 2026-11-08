# Audio Control for Home Assistant — balena template

[![Deploy with balena](https://balena.io/deploy.svg)](https://dashboard.balena-cloud.com/deploy?repoUrl=https://github.com/mcjelcom/haac-balena)

Home Assistant with the [Audio Control](https://github.com/mcjelcom/ha-audio-control)
integration already installed, deployed to a Raspberry Pi through
[balenaCloud](https://www.balena.io/cloud). Use this if you want to manage the Pi
remotely or look after several of them. For one Pi at home, the standard Home
Assistant OS install is simpler.

**Guide (with pictures):** https://haac.mcjel.com/getting-started/install-balena/ ·
**Which install should I use?** https://haac.mcjel.com/getting-started/choose-install/

## What's inside

| | |
|---|---|
| Home Assistant | `2026.10.2` (Container) |
| Audio Control | `2.0.14` (download checked against its SHA-256) |
| Dashboard | **Audio Control** in the sidebar — one card per zone, All Off and Group buttons, built automatically once you add your amplifier |
| Blueprints | From the same Audio Control release: ready-made automations (all zones off at a time, scheduled zone on, volume limiter, …) under Settings → Automations → Blueprints |
| Matter (optional) | Home Assistant Matter Hub `2.0.59` — **off** until you enable it (below) |
| Devices | Raspberry Pi 4 / 5 (64-bit), Raspberry Pi 3 (64-bit) |

One service only. Home Assistant uses host networking so it can find devices on
your network; it is reachable at `http://<device-ip>:8123` on your local network
and protected by its own login. Nothing else is exposed (no SSH, no file editor).
It runs privileged so any USB-to-RS232 adapter you plug in is visible.

## Your dashboard

The template adds an **Audio Control** dashboard to the sidebar. Once you add your
amplifier it fills in by itself with one card per zone, named after your zones. It
is regenerated when the integration restarts; to keep your own edits, delete the
first line (`# audio_control:managed`) of `dashboards/audio_control.yaml` and it is
never touched again. If your `configuration.yaml` already has a `lovelace:` section,
the template leaves it alone and prints the lines to add in the log.

## Matter (optional, off by default)

Shares your zones over Matter with Google Home, Alexa, SmartThings and Aqara
([what works](https://haac.mcjel.com/matter/)). To turn it on, add these **device
variables** in the balena dashboard (Device → Variables), for the `matter-hub` service:

| Variable | Value |
|---|---|
| `HAAC_MATTER` | `1` |
| `HAMH_HOME_ASSISTANT_ACCESS_TOKEN` | a long-lived token: Home Assistant → your profile → **Security** → *Create token* |
| `HAMH_HTTP_AUTH_USERNAME` | a username for the bridge's web page |
| `HAMH_HTTP_AUTH_PASSWORD` | a password, **12+ characters** |

Then open `http://<device-ip>:8482`, log in, and create a bridge. Without all four the
service stays idle and opens no port. When on, it listens on your home network on TCP
8482 (web page, login required — it shows the pairing code) and UDP 5540 (Matter,
protected by the pairing code).

## Updates

Audio Control and Home Assistant are updated by **new releases of this
template**, not from inside Home Assistant (there is no Supervisor on balena).
Don't also install Audio Control from HACS on these devices — the bundled copy
replaces it on every start.

## License

[MIT](LICENSE) © McJEL, LLC
