"""End-to-end smoke test of the built image, the way a new user meets it.

Starts from a fresh /config: completes onboarding over the HTTP API, adds an
Audio Control amplifier in `demo` mode through the real config flow, and checks
that its zones appear as media players. Stdlib only; run against a container
started with `-p 127.0.0.1:8123:8123` (see .github/workflows/ci.yml).

Usage: python3 tests/smoke.py [base_url]
"""

from __future__ import annotations

import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123"
CLIENT_ID = f"{BASE}/"


def request(path: str, data: object = None, token: str = "", form: bool = False) -> object:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    body = None
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()  # type: ignore[arg-type]
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read() or b"null")


def wait_for_onboarding(timeout: float = 600) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            request("/api/onboarding")
            return
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(5)
    sys.exit("FAIL: Home Assistant did not come up")


def main() -> None:
    wait_for_onboarding()
    password = secrets.token_urlsafe(16)
    user = request(
        "/api/onboarding/users",
        {"client_id": CLIENT_ID, "name": "Smoke", "username": "smoke",
         "password": password, "language": "en"},
    )
    token = request(
        "/auth/token",
        {"grant_type": "authorization_code", "code": user["auth_code"],  # type: ignore[index]
         "client_id": CLIENT_ID},
        form=True,
    )["access_token"]  # type: ignore[index]

    # Integration loads and offers its config flow.
    flow = request(
        "/api/config/config_entries/flow",
        {"handler": "audio_control", "show_advanced_options": False}, token,
    )
    assert flow["type"] == "form", flow  # type: ignore[index]
    fields = {f["name"]: f for f in flow["data_schema"]}  # type: ignore[index]
    profile_field = next(f for n, f in fields.items() if "profile" in n)
    options = [o[0] if isinstance(o, list) else o for o in profile_field.get("options", [])]
    if not options:  # selector-style schema
        options = [o["value"] for o in profile_field["selector"]["select"]["options"]]
    device = next(o for o in options if "X86" in o)
    done = request(
        f"/api/config/config_entries/flow/{flow['flow_id']}",  # type: ignore[index]
        {profile_field["name"]: device, "port": "demo"}, token,
    )
    assert done["type"] == "create_entry", done  # type: ignore[index]

    zones: list[dict[str, object]] = []
    for _ in range(30):
        states = request("/api/states", token=token)
        zones = [s for s in states if str(s["entity_id"]).startswith("media_player.")]  # type: ignore[union-attr,index]
        if zones:
            break
        time.sleep(2)
    assert zones, "no media_player entities appeared"

    print(f"PASS: '{device}' in demo mode -> {len(zones)} zones")


if __name__ == "__main__":
    main()
