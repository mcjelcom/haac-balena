# Matter round-trip test (manual)

Pairs a [matter.js](https://github.com/project-chip/matter.js) controller with a
Home Assistant Matter Hub bridge and drives Audio Control zones over Matter, checking
Home Assistant's state after each command (Speaker on/off, volume, source; Plug on/off).

Run everything inside the HA container's network namespace (nothing is published):

1. Start the template image as in `tests/smoke.py` and add the demo amplifier.
2. Create `switch.living_room_music` / `switch.kitchen_music` (Template → Switch helpers).
3. `docker run --network container:<ha> -e HAMH_HOME_ASSISTANT_URL=http://127.0.0.1:8123
   -e HAMH_HOME_ASSISTANT_ACCESS_TOKEN=<long-lived token> ghcr.io/riddix/home-assistant-matter-hub:2.0.59`
4. Create a bridge (POST `/api/matter/bridges` on :8482) including platform `audio_control`
   and pattern `switch.*_music`, excluding domain `binary_sensor`.
5. `npm i @matter/main @project-chip/matter.js` (0.18.0 tested), then
   `docker run --network container:<ha> -e HA_TOKEN=<token> -v $PWD:/w -w /w node:22 node roundtrip.mjs <passcode> <discriminator>`

Last run 2026-11-08: ALL PASS (Matter Hub 2.0.59, matter.js 0.18.0, HA 2026.10.2).
