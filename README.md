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
| Audio Control | `2.0.12` (download checked against its SHA-256) |
| Devices | Raspberry Pi 4 / 5 (64-bit), Raspberry Pi 3 (64-bit) |

One service only. Home Assistant uses host networking so it can find devices on
your network; it is reachable at `http://<device-ip>:8123` on your local network
and protected by its own login. Nothing else is exposed (no SSH, no file editor).
It runs privileged so any USB-to-RS232 adapter you plug in is visible.

## Updates

Audio Control and Home Assistant are updated by **new releases of this
template**, not from inside Home Assistant (there is no Supervisor on balena).
Don't also install Audio Control from HACS on these devices — the bundled copy
replaces it on every start.

## License

[MIT](LICENSE) © McJEL, LLC
