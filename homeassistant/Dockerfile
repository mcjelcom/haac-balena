# Home Assistant (Container) + the Audio Control integration, for balena.
#
# Both are PINNED: a floating tag would pull a new Home Assistant on any deploy.
# A template release bumps them deliberately, together with the tests in CI.
FROM homeassistant/home-assistant:2026.10.2

# Audio Control release, pinned to its tag AND the tarball's SHA-256 so a moved
# tag or a tampered download fails the build instead of shipping.
# Bump: change both ARGs together:
#   curl -sL https://github.com/mcjelcom/ha-audio-control/archive/refs/tags/v<X>.tar.gz | shasum -a 256
ARG AUDIO_CONTROL_VERSION=2.0.13
ARG AUDIO_CONTROL_SHA256=3a4d79ce455405fe201e7a14d317b29da33224df3f4f06be96b543d5e1f73da2

RUN wget -q -O /tmp/ac.tgz \
      "https://github.com/mcjelcom/ha-audio-control/archive/refs/tags/v${AUDIO_CONTROL_VERSION}.tar.gz" && \
    echo "${AUDIO_CONTROL_SHA256}  /tmp/ac.tgz" | sha256sum -c - && \
    mkdir -p /tmp/ac-src /opt/haac && tar -xzf /tmp/ac.tgz -C /tmp/ac-src && \
    cp -r "/tmp/ac-src/ha-audio-control-${AUDIO_CONTROL_VERSION}/custom_components/audio_control" \
          /opt/haac/audio_control && \
    grep -q "\"version\": \"${AUDIO_CONTROL_VERSION}\"" /opt/haac/audio_control/manifest.json && \
    rm -rf /tmp/ac.tgz /tmp/ac-src

# The integration's only Python requirement, installed at build time so the
# first start does not need to download it. Quoted: unquoted, `>=` is a shell
# redirect and the pin would be silently dropped.
RUN pip install --no-cache-dir "pyserial-asyncio-fast>=0.11"

# Fail the build, not the device, if the bundled device profiles went missing.
RUN python -c "import sys; sys.path.insert(0, '/opt/haac/audio_control'); \
from rs232_protocol.profile_loader import load_builtin_profiles; \
n = len(load_builtin_profiles()); print('Audio Control profiles:', n); \
assert n >= 20, n"

COPY start.sh /usr/local/bin/haac-start.sh
COPY provision.py /usr/local/bin/haac-provision.py
COPY blueprints /opt/haac/blueprints
RUN chmod +x /usr/local/bin/haac-start.sh && \
    test -f /opt/haac/audio_control/dashboard.yaml

CMD ["/usr/local/bin/haac-start.sh"]
