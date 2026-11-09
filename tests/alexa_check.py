"""Alexa Smart Home check: send Alexa's own directives to HA's handler.

HA Cloud forwards every Alexa command to homeassistant.components.alexa.smart_home;
with `alexa: smart_home:` in configuration.yaml the same handler is reachable at
/api/alexa/smart_home. Expects a demo zone whose sources include "Tuner".
Usage: python3 tests/alexa_check.py <base_url> <tokens.json>
"""
import json, os, sys, time, urllib.request, uuid
B = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123"
T = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "/tmp/ha_tokens.json"))["access_token"]; H = {"Authorization": f"Bearer {T}", "Content-Type": "application/json"}
EP = "media_player#amc_x86_x86i_zone_1"; MP = "media_player.amc_x86_x86i_zone_1"
def directive(ns, name, payload=None, endpoint=True):
    d = {"directive": {"header": {"namespace": ns, "name": name, "payloadVersion": "3", "messageId": str(uuid.uuid4()), "correlationToken": "t"},
                       "payload": payload or {}}}
    if endpoint: d["directive"]["endpoint"] = {"endpointId": EP, "scope": {"type": "BearerToken", "token": T}}
    else: d["directive"]["payload"] = {"scope": {"type": "BearerToken", "token": T}}
    r = urllib.request.urlopen(urllib.request.Request(B + "/api/alexa/smart_home", json.dumps(d).encode(), H), timeout=30)
    return json.loads(r.read())
def state():
    s = json.load(urllib.request.urlopen(urllib.request.Request(f"{B}/api/states/{MP}", headers=H)))
    a = s["attributes"]; return f"{s['state']} vol={a.get('volume_level')} muted={a.get('is_volume_muted')} src={a.get('source')}"
disc = directive("Alexa.Discovery", "Discover", endpoint=False)
ep = next(e for e in disc["event"]["payload"]["endpoints"] if e["endpointId"] == EP)
print("Discovery for", ep["friendlyName"], "| category:", ep["displayCategories"])
for c in ep["capabilities"]:
    if c["interface"] == "Alexa": continue
    extra = ""
    if c["interface"] == "Alexa.InputController": extra = " inputs=" + ",".join(i["name"] for i in c.get("inputs", []))
    print("  ", c["interface"] + extra)
tests = [
    ("Alexa.PowerController", "TurnOn", {}, lambda s: s.startswith("on")),
    ("Alexa.Speaker", "SetVolume", {"volume": 60}, lambda s: "vol=0.5" in s or "vol=0.6" in s),
    ("Alexa.Speaker", "AdjustVolume", {"volume": -20, "volumeDefault": False}, lambda s: "vol=0.3" in s or "vol=0.4" in s),
    ("Alexa.StepSpeaker", "AdjustVolume", {"volumeSteps": 2}, lambda s: True),
    ("Alexa.Speaker", "SetMute", {"mute": True}, lambda s: "muted=True" in s),
    ("Alexa.Speaker", "SetMute", {"mute": False}, lambda s: "muted=False" in s),
    ("Alexa.InputController", "SelectInput", {"input": "Tuner"}, lambda s: "src=Tuner" in s),
    ("Alexa.PowerController", "TurnOff", {}, lambda s: s.startswith("off")),
]
caps = {c["interface"] for c in ep["capabilities"]}
results = []
for ns, name, payload, ok in tests:
    if ns not in caps: print(f"SKIP  {ns}.{name} (not offered to Alexa)"); continue
    r = directive(ns, name, payload); time.sleep(1.5)
    hdr = r["event"]["header"]["name"]; st = state()
    good = hdr != "ErrorResponse" and ok(st)
    detail = r["event"]["payload"].get("message", "") if hdr == "ErrorResponse" else ""
    results.append(good); print(f"{'PASS' if good else 'FAIL'}  {ns}.{name} {payload} -> {hdr} | {st} {detail}")

missing = {"Alexa.PowerController", "Alexa.Speaker", "Alexa.InputController"} - caps
if missing or not results or not all(results):
    sys.exit(f"ALEXA CHECK FAILED (missing interfaces: {sorted(missing)})")
print("ALEXA CHECK PASS")
