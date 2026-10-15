#!/bin/bash
# Mide el rendimiento de SMUSH! en tu iPhone (cuadros por segundo reales) y luego deja la app normal otra vez.
# Úsalo después de agregar cosas pesadas: si algo baja de 60 fps, se ve aquí.
# Uso: ./perf-on-iphone.sh     (iPhone conectado por cable, desbloqueado). Tarda ~3 min; no toques el teléfono.
# Qué mide (perf-probe.js): el Inicio y el swipe de islas; en cada nivel quieto, tocando, con la Sierra y con las demás
# herramientas (todo al máximo, solo en memoria: tu partida no cambia); la Tienda y la vitrina abiertas.
# fps = cuadros por segundo · p95 = el 5 % más lento (ms; 17 = perfecto) · long = cuadros que se saltaron (>25 ms; un salto se ve como ~33 ms) · js = ms del código por cuadro
set -e
cd "$(dirname "$0")"
OUT=$(mktemp -t smush-perf)
PERF=1 ./run-on-iphone.sh
DEV=$(python3 -c '
import json, subprocess
subprocess.run(["xcrun", "devicectl", "list", "devices", "--json-output", "/tmp/smush-devices.json"], capture_output=True)
d = json.load(open("/tmp/smush-devices.json"))["result"]["devices"]
d = [x for x in d if x.get("hardwareProperties", {}).get("platform") == "iOS" and x.get("connectionProperties", {}).get("pairingState") == "paired"]
d.sort(key=lambda x: x.get("connectionProperties", {}).get("transportType") != "wired")
print(d[0]["identifier"] if d else "")
')
echo "Midiendo (~3 min, no toques el teléfono)…"
xcrun devicectl device process launch --console --terminate-existing --device "$DEV" com.blubergames.smush > "$OUT" 2>&1 &
PID=$!
for i in $(seq 1 80); do sleep 5; grep -q '"done"' "$OUT" && break; done
kill $PID 2>/dev/null || true
echo
python3 - "$OUT" <<'PY'
import json, sys
for line in open(sys.argv[1], errors="ignore"):
    if "PERF " not in line: continue
    o = json.loads(line.split("PERF ", 1)[1])
    if "label" not in o: continue
    bad = "  <- se atora" if o["fps"] < 57 or o["long"] > 6 else ""
    js = "-" if o["js"] is None else o["js"]
    print("%-16s %5s fps   p95 %5s ms   long %3s   js %5s ms%s" % (o["label"], o["fps"], o["p95"], o["long"], js, bad))
PY
echo
echo "Regresando la app normal…"
./run-on-iphone.sh | tail -1
