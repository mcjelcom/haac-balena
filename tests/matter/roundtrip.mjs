// Manual Matter round-trip test (not run in CI yet). Usage: see tests/matter/README.md
// Pair with the Matter Hub bridge as a Matter controller, then drive zones over
// Matter and check Home Assistant's real state after each command.
import { Environment } from "@matter/main";
import { CommissioningController } from "@project-chip/matter.js";
import { GeneralCommissioning, OnOff, LevelControl, MediaInput, BridgedDeviceBasicInformation } from "@matter/main/clusters";

const [passcode, discriminator] = process.argv.slice(2).map(Number);
const HA = "http://127.0.0.1:8123", TOKEN = process.env.HA_TOKEN;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const state = async e => (await (await fetch(`${HA}/api/states/${e}`, { headers: { Authorization: `Bearer ${TOKEN}` } })).json());
const results = [];
const check = (name, ok, detail) => { results.push([name, ok]); console.log(`${ok ? "PASS" : "FAIL"}  ${name}  (${detail})`); };

const env = Environment.default;
env.vars.set("storage.path", "/w/storage");
const controller = new CommissioningController({ environment: { environment: env, id: "haac-test-controller" }, autoConnect: false, adminFabricLabel: "haac-test" });
await controller.start();
let nodeId = controller.getCommissionedNodes()[0];
if (nodeId === undefined) {
  nodeId = await controller.commissionNode({
    commissioning: { regulatoryLocation: GeneralCommissioning.RegulatoryLocationType.IndoorOutdoor, regulatoryCountryCode: "XX" },
    discovery: { knownAddress: { ip: "127.0.0.1", port: 5540, type: "udp" }, identifierData: { longDiscriminator: discriminator } },
    passcode,
  });
  console.log("commissioned node", nodeId.toString());
}
const node = await controller.connectNode(nodeId);
for (let i = 0; i < 60 && node.getDevices().length === 0; i++) await sleep(500);
const byLabel = {};
const visit = ep => {
  const bi = ep.getClusterClient(BridgedDeviceBasicInformation.Cluster);
  if (bi) byLabel[ep.number] = ep;
  for (const p of ep.parts.values()) visit(p);
};
for (const d of node.getDevices()) visit(d);
const labels = {};
for (const [num, ep] of Object.entries(byLabel)) labels[await ep.getClusterClient(BridgedDeviceBasicInformation.Cluster).getNodeLabelAttribute()] = ep;
console.log("bridged:", Object.keys(labels).join(" | "));

const zone = Object.entries(labels).find(([l]) => l.endsWith("Living Room"))[1];
const plug = labels["Kitchen Music"];
const LR = "media_player.amc_x86_x86i_zone_1", K = "media_player.amc_x86_x86i_zone_2";

await zone.getClusterClient(OnOff.Cluster).on(); await sleep(2500);
check("Speaker on/off: on", (await state(LR)).state === "on", (await state(LR)).state);
await zone.getClusterClient(LevelControl.Cluster).moveToLevel({ level: 127, transitionTime: 0, optionsMask: {}, optionsOverride: {} }); await sleep(2500);
const vol = (await state(LR)).attributes.volume_level;
check("Speaker volume -> 50%", vol > 0.4 && vol < 0.6, `volume_level=${vol}`);
const mi = zone.getClusterClient(MediaInput.Cluster);
const inputs = await mi.getInputListAttribute();
const spotify = inputs.find(i => i.name === "Spotify");
await mi.selectInput({ index: spotify.index }); await sleep(2500);
const src = (await state(LR)).attributes.source;
check("Speaker source -> Spotify", src === "Spotify", `source=${src}; inputs=${inputs.map(i => i.name).join(",")}`);
await zone.getClusterClient(OnOff.Cluster).off(); await sleep(2500);
check("Speaker on/off: off", (await state(LR)).state === "off", (await state(LR)).state);

await plug.getClusterClient(OnOff.Cluster).on(); await sleep(2500);
check("Plug 'Kitchen Music' on -> Kitchen zone on", (await state(K)).state === "on", (await state(K)).state);
await plug.getClusterClient(OnOff.Cluster).off(); await sleep(2500);
check("Plug off -> Kitchen zone off", (await state(K)).state === "off", (await state(K)).state);

console.log(results.every(([, ok]) => ok) ? "ALL PASS" : "SOME FAILED");
await controller.close();
process.exit(0);
