#!/bin/sh
# Opt-in, and fail closed. Set these as balena device (or fleet) variables:
#   HAAC_MATTER=1
#   HAMH_HOME_ASSISTANT_ACCESS_TOKEN   a long-lived token (HA: your profile -> Security)
#   HAMH_HTTP_AUTH_USERNAME / HAMH_HTTP_AUTH_PASSWORD   login for the bridge's web page
#                                      (it shows the pairing code), 12+ characters
# While off or misconfigured the container idles (no restart loop) and opens no port.
idle() { echo "[haac-matter] $*"; exec sleep infinity; }

[ "${HAAC_MATTER:-0}" = "1" ] || idle "off -- set the device variable HAAC_MATTER=1 to enable"
[ -n "${HAMH_HOME_ASSISTANT_ACCESS_TOKEN:-}" ] || \
    idle "NOT STARTING: set HAMH_HOME_ASSISTANT_ACCESS_TOKEN (a long-lived token from your Home Assistant profile)"
[ -n "${HAMH_HTTP_AUTH_USERNAME:-}" ] || idle "NOT STARTING: set HAMH_HTTP_AUTH_USERNAME"
[ "${#HAMH_HTTP_AUTH_PASSWORD}" -ge 12 ] 2>/dev/null || \
    idle "NOT STARTING: set HAMH_HTTP_AUTH_PASSWORD (at least 12 characters)"

export HAMH_HOME_ASSISTANT_URL="${HAMH_HOME_ASSISTANT_URL:-http://127.0.0.1:8123}"
export HAMH_STORAGE_LOCATION="${HAMH_STORAGE_LOCATION:-/data}"
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=384}"
echo "[haac-matter] starting Matter Hub (web page login required)"
exec home-assistant-matter-hub start
