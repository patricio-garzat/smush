// Capturas del juego para la App Store, en Chrome sin ventana y en alta resolución.
// Uso: node --experimental-websocket store/shots.js <phone|ipad> <en|es> [escena,escena…]   (con el servidor local en :8791)
// Sale en store/raw/<device>-<lang>-<escena>.png. El juego se congela en el cuadro exacto (STEP avanza a mano).
const { spawn } = require("child_process"), fs = require("fs"), path = require("path");
const [device, lang, only] = process.argv.slice(2);
const DEV = { phone: { w: 402, h: 874, dpr: 3 }, ipad: { w: 1180, h: 820, dpr: 3 } }[device];
const OUT = path.join(__dirname, "raw");
const URL = "http://localhost:8791/Smush/index.html";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Cada escena: partida guardada, tema y lo que pasa antes de la foto (en la página)
const SCENES = {
  squish: { theme: "light", save: { level: 1, tools: { finger: 6, bolt: 2, saw: 1, bomb: 2, wave: 1 }, tool: "finger", up: { crowd: 12 } }, run: `
    STEP(6);
    for (let k = 0; k < 16; k++) {
      const live = balls.filter((b) => b.state !== "die" && b.entered && b.y > H * 0.28 && b.y < H * 0.86 && b.x > 40 && b.x < W - 40);
      const b = live[(k * 7) % Math.max(1, live.length)]; if (b) useTool(b.x, b.y, 1);
      STEP(k < 13 ? 0.11 : 0.06);
    }` },
  train: { theme: "light", save: { level: 5, tools: { finger: 6, bolt: 4, saw: 2, bomb: 3, meteor: 1, train: 1 }, tool: "train" }, run: `
    STEP(7); useTool(W / 2, H / 2, 1); STEP(+(window.TRAIN_T || 2.3));` },
  helpers: { theme: "dark", save: { level: 2, tools: { finger: 6, bolt: 5, saw: 2, bomb: 3, wave: 1, meteor: 1, aval: 1 }, tool: "bolt", up: { hire: 1, carea: 12, cchain: 12, crowd: 10, fingers: 2, fspeed: 6 } }, run: `
    STEP(9); for (let i = 0; i < 80 && bolts.length < 3; i++) STEP(0.05);` },
  shop: { theme: "light", save: { level: 0, tools: { finger: 7, bolt: 5, saw: 2 }, tool: "finger", up: { hire: 1, carea: 9, cchain: 7, fingers: 2, fspeed: 5, value: 6, crowd: 4 } }, sheet: "shop", run: `
    STEP(5); window.requestAnimationFrame = RAF0; shopTab = "helpers"; $("#btn-shop").click();` },
  trophies: { theme: "dark", save: { level: 3, tools: { finger: 6, bolt: 4, car: 1 }, tool: "finger" }, sheet: "goals", run: `
    STEP(4); window.requestAnimationFrame = RAF0; ACH.forEach((a, i) => { const [c, t] = a.prog(); if (c >= t || (a.grp !== "smush" && a.grp !== "spent" && i % 3 !== 1)) save.g.ach[a.id] = Date.now(); }); openGoals("ach");` },
  city: { theme: "dark", save: { level: 3, tools: { finger: 6, bolt: 4, saw: 2, bomb: 3, meteor: 1, car: 1 }, tool: "car", up: { hire: 1, carea: 6, cchain: 6 } }, run: `
    STEP(7); useTool(W / 2, H / 2, 1); STEP(+(window.CAR_T || 1.7));` },
};

const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=" + (9500 + Math.floor(Math.random() * 300)), "--user-data-dir=/tmp/smush-shots-" + Date.now(), "--hide-scrollbars", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
let port; chrome.stderr.on("data", (d) => { const m = /127\.0\.0\.1:(\d+)/.exec(String(d)); if (m) port = m[1]; });
(async () => {
  for (let i = 0; i < 60 && !port; i++) await sleep(200);
  let tabs; for (let i = 0; i < 40; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await sleep(250); } }
  const page = tabs.find((t) => t.type === "page"), ws = new WebSocket(page.webSocketDebuggerUrl); let id = 0; const pend = new Map();
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
  await new Promise((r) => (ws.onopen = r));
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 1200)); return r.result.result.value; };
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: DEV.w, height: DEV.h, deviceScaleFactor: DEV.dpr, mobile: true });
  await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
  fs.mkdirSync(OUT, { recursive: true });
  for (const name of (only ? only.split(",") : Object.keys(SCENES))) {
    const S = SCENES[name];
    await send("Page.navigate", { url: URL }); await sleep(1200);
    const save = { coins: [184500, 245000, 1830000, 7420000, 26900000, 96400000][S.save.level], earned: 1e10, smushed: [14200, 31200, 64800, 112400, 176500, 251300][S.save.level], v: 7, up: {}, hinted: true, readyAsked: 9, ...S.save };
    // Se escribe la partida y se bloquea el guardado de esta página (si no, al recargar el juego guarda la suya encima)
    await ev(`(() => { const set = Storage.prototype.setItem; set.call(localStorage, "smush-save-v1", ${JSON.stringify(JSON.stringify(save))}); set.call(localStorage, "smush-settings-v1", ${JSON.stringify(JSON.stringify({ theme: S.theme, lang, mv: 3, sound: false, music: false, haptics: false }))}); Storage.prototype.setItem = function () {}; return 1; })()`);
    await send("Page.navigate", { url: URL }); await sleep(2500);
    await ev(`(() => {
      ["splash", "studio"].forEach((i) => { const e = document.getElementById(i); if (e) e.remove(); });
      const st = document.createElement("style"); st.textContent = "#toasts{display:none!important} *{caret-color:transparent}"; document.head.appendChild(st);
      (0, eval)(resize.toString().replace("Math.min(window.devicePixelRatio || 1, 2)", "${DEV.dpr}"));
      window.__now = 0; window.RAF0 = window.requestAnimationFrame;
      window.STEP = (s) => { cancelAnimationFrame(raf); if (!__now) __now = Math.max(last || 0, performance.now()); window.requestAnimationFrame = () => 0; for (let i = 0; i < Math.round(s * 60); i++) { __now += 1000 / 60; loop(__now); } };
      enterGame(); resize(); return 1; })()`);
    await sleep(900);
    await ev(`document.fonts.ready.then(() => 1)`);
    await ev(`(() => { ${S.run}; return 1; })()`);
    await sleep(S.sheet ? 1600 : 400);
    const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const file = path.join(OUT, `${device}-${lang}-${name}.png`);
    fs.writeFileSync(file, Buffer.from(shot.result.data, "base64"));
    console.log("ok", path.basename(file));
  }
  ws.close(); chrome.kill();
})().catch((e) => { console.error("ERR", e.message); chrome.kill(); process.exit(1); });
