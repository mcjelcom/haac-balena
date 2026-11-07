#!/usr/bin/env bash
# Install the bundled Audio Control into /config, then start Home Assistant.
#
# Runs on every start, so a new template release (new image) also updates the
# integration. The bundled copy wins over one installed through HACS: on
# balena, Audio Control is updated by deploying a new template release.
set -euo pipefail

src=/opt/haac/audio_control
dst=/config/custom_components/audio_control

mkdir -p /config/custom_components
rm -rf "${dst}.new"
cp -r "$src" "${dst}.new"
rm -rf "$dst"
mv "${dst}.new" "$dst"
echo "[haac] Audio Control $(python -c "import json; print(json.load(open('$dst/manifest.json'))['version'])") installed"

exec python -m homeassistant --config /config
