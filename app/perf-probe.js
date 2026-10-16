// Prueba de rendimiento SOLO para medir en el iPhone (no va en la app normal ni en la web).
// Se corre con ./perf-on-iphone.sh (la mete build-www.py con PERF=1)
// No guarda nada: tu partida del celular queda igual. Escribe los resultados en la consola ("PERF …").
(function () {
  Storage.prototype.setItem = function () {}; // nada se guarda mientras se mide
  const log = (o) => console.log("PERF " + JSON.stringify(o));
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  // Mide los cuadros reales (requestAnimationFrame) y cuánto tarda el código del juego en cada uno
  async function measure(label, ms) {
    const gaps = []; window.__jsMax = 0;
    let prev = 0, on = true;
    const tick = (t) => { if (prev) gaps.push(t - prev); prev = t; if (on) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
    window.__js = 0; window.__jsN = 0;
    await wait(ms);
    on = false;
    gaps.sort((a, b) => a - b);
    const n = gaps.length, sum = gaps.reduce((a, b) => a + b, 0);
    log({ label, fps: +(1000 * n / sum).toFixed(1), p50: +gaps[n >> 1].toFixed(1), p95: +gaps[Math.floor(n * 0.95)].toFixed(1), max: +gaps[n - 1].toFixed(1), long: gaps.filter((g) => g > 25).length, frames: n, js: window.__jsN ? +(window.__js / window.__jsN).toFixed(2) : null, jsMax: +window.__jsMax.toFixed(1), balls: typeof balls !== "undefined" ? balls.length : null });
  }
  const noBlur = document.createElement("style");
  noBlur.textContent = "*, *::before, *::after { -webkit-backdrop-filter: none !important; backdrop-filter: none !important; }";
  window.addEventListener("load", async () => {
    // El tiempo del código del juego por cuadro
    const realLoop = window.loop;
    window.loop = function (now) { const t = performance.now(); realLoop(now); const d = performance.now() - t; window.__js += d; window.__jsN++; if (d > window.__jsMax) window.__jsMax = d; };
    log({ start: true, ua: navigator.userAgent, dpr: devicePixelRatio, w: innerWidth, h: innerHeight });
    await wait(11000); // las intros
    await measure("home", 5000);
    // Swipe de islas en el Inicio
    if (typeof Hero !== "undefined") { const r = document.getElementById("home-cv").getBoundingClientRect(); const sw = async () => { const id = ++window.__hp; const e = (t, x) => document.getElementById("home-cv").dispatchEvent(new PointerEvent(t, { bubbles: true, clientX: x, clientY: r.top + r.height / 2, pointerId: id, pointerType: "touch", isPrimary: true })); e("pointerdown", r.left + r.width * 0.8); for (let i = 1; i <= 8; i++) { await wait(16); e("pointermove", r.left + r.width * (0.8 - i * 0.07)); } e("pointerup", r.left + r.width * 0.24); }; window.__hp = 900; await Promise.all([measure("home swipe", 6000), (async () => { for (let i = 0; i < 3; i++) { await sw(); await wait(1800); } })()]); }
    // Lo más pesado posible: todas las herramientas y ayudantes al máximo (solo en memoria)
    for (const k in save.tools) save.tools[k] = TOOLS[k].max || 3;
    for (const k in save.up) save.up[k] = upMax(k);
    save.off = {};
    enterGame();
    await wait(1500);
    // Toques de mentira sobre el campo (como si jugaras): pasan por los mismos eventos que un dedo de verdad
    let pid = 100;
    const ev = (type, x, y, id) => { const r = cv.getBoundingClientRect(); cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y, pointerId: id, pointerType: "touch", isPrimary: true })); };
    const target = () => { const live = balls.filter((b) => b.state !== "die" && b.entered); const b = live[Math.floor(Math.random() * live.length)]; return b ? [b.x, b.y] : [W / 2, H / 2]; };
    async function taps(perSec, ms) {
      const end = performance.now() + ms;
      while (performance.now() < end) { const [x, y] = target(), id = ++pid; ev("pointerdown", x, y, id); await wait(40); ev("pointerup", x, y, id); await wait(1000 / perSec - 40); }
    }
    async function drag(ms) {
      const id = ++pid, end = performance.now() + ms; let [x, y] = target(); ev("pointerdown", x, y, id);
      while (performance.now() < end) { const [tx, ty] = target(); for (let i = 0; i < 12; i++) { x += (tx - x) * 0.15; y += (ty - y) * 0.15; ev("pointermove", x, y, id); await wait(16); } }
      ev("pointerup", x, y, id);
    }
    const play = (label, fn) => Promise.all([measure(label, 6000), fn()]);
    for (const lv of [0, 1, 2, 3, 4]) {
      save.level = lv; resetWorld(); applyLevel(); ensureBg();
      await wait(3500);
      const L = lvl().id;
      await measure(L + " idle", 4000);
      save.tool = "finger"; await play(L + " tap", () => taps(7, 6000));
      save.tool = "saw"; await play(L + " saw", () => drag(6000));
      const tools = TOOL_ORDER.filter((k) => k !== "finger" && k !== "saw" && (!TOOLS[k].world || TOOLS[k].world <= lv) && (TOOLS[k].only == null || TOOLS[k].only === lv));
      await play(L + " tools", async () => { for (let i = 0; i < 12; i++) { save.tool = tools[i % tools.length]; await taps(2, 500); } });
      save.tool = "finger";
    }
    // La avalancha y el tsunami completos (de que se sueltan a que se van)
    save.level = 2; resetWorld(); applyLevel(); ensureBg(); await wait(3500);
    await Promise.all([measure("avalanche", 7000), (async () => { save.tool = "aval"; cdEnd.aval = 0; useTool(W / 2, H / 2); })()]);
    save.level = 1; resetWorld(); applyLevel(); ensureBg(); await wait(3500);
    await Promise.all([measure("tsunami", 7000), (async () => { save.tool = "wave"; cdEnd.wave = 0; useTool(W / 2, H / 2); })()]);
    save.tool = "finger";
    // Hojas abiertas mientras el juego corre debajo
    openSheet(document.getElementById("sheet-shop")); await wait(800);
    const body = document.getElementById("shop-body");
    await Promise.all([measure("shop scroll", 5000), (async () => { for (let i = 0; i < 60; i++) { if (body) body.scrollTop = (i % 20) * 40; await wait(80); } })()]);
    closeSheet(document.getElementById("sheet-shop")); await wait(800);
    openGoals("ach"); await wait(800);
    await measure("trophies", 4000);
    closeSheet(document.getElementById("sheet-goals")); await wait(800);
    showHome(); await wait(1500);
    await measure("home after", 4000);
    // El viaje en avión (solo en memoria): de la isla 1 a la 2
    save.level = 0; resetWorld(); applyLevel(); ensureBg(); enterGame(); await wait(1500);
    save.smushed = 1e6; save.coins = 1e12;
    await Promise.all([measure("trip", 4500), (async () => { travel(); })()]);
    log({ done: true });
  });
})();
