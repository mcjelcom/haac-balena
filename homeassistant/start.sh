#!/usr/bin/env bash
# Install the bundled Audio Control (+ its dashboard and blueprints) into
# /config, then start Home Assistant.
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

# Dashboard: install the starter file only if there is none, or if it is still
# ours (first line `# audio_control:managed`). The integration then fills it
# with one card per zone once your amplifier is added. Delete that first line
# to keep your own edits -- nothing here or in the integration touches it again.
mkdir -p /config/dashboards
dash=/config/dashboards/audio_control.yaml
if [ ! -f "$dash" ]; then
    cp "$src/dashboard.yaml" "$dash"
    echo "[haac] dashboard installed"
elif ! head -c 512 "$dash" | grep -q "audio_control:managed"; then
    echo "[haac] dashboard is yours (managed line removed), leaving it alone"
fi
python /usr/local/bin/haac-provision.py

# Blueprints: only offered in Settings -> Automations -> Blueprints until you use
# one. Replaced every start (our own folder only) so updates arrive.
mkdir -p /config/blueprints/automation
rm -rf /config/blueprints/automation/audio_control
cp -r /opt/haac/blueprints/automation/audio_control /config/blueprints/automation/

exec python -m homeassistant --config /config
