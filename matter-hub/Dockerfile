# Optional Matter bridge for the Audio Control zones (docs: haac.mcjel.com/matter/).
# Home Assistant Matter Hub, pinned by version AND digest. OFF unless the device
# variable HAAC_MATTER=1 is set, and it refuses to start without a web-page login.
FROM ghcr.io/riddix/home-assistant-matter-hub:2.0.59@sha256:ef997a84c088ac89e57f9cde0fb6fd18447da0a3c8cc9466c4232ba5a15bd9d7
COPY haac-matter-start.sh /usr/local/bin/haac-matter-start.sh
RUN chmod +x /usr/local/bin/haac-matter-start.sh
CMD ["/usr/local/bin/haac-matter-start.sh"]
