#!/bin/bash
# Instala SMUSH! en tu iPhone para probarlo (no sube nada a la App Store).
# Toma el juego de ../index.html (el mismo de la web), arma la app, la compila firmada con tu equipo y la abre.
# Uso: ./run-on-iphone.sh     (con el iPhone conectado por cable, desbloqueado y con Modo de desarrollador)
set -e
cd "$(dirname "$0")"

echo "1/4 · Armando la app con el juego de la web…"
npm run build --silent

echo "2/4 · Buscando tu iPhone…"
IDS=$(xcrun devicectl list devices --json-output /tmp/smush-devices.json >/dev/null 2>&1; python3 -c '
import json
d = json.load(open("/tmp/smush-devices.json"))["result"]["devices"]
d = [x for x in d if x.get("hardwareProperties", {}).get("platform") == "iOS" and x.get("connectionProperties", {}).get("pairingState") == "paired"]
d.sort(key=lambda x: x.get("connectionProperties", {}).get("transportType") != "wired")
print(d[0]["hardwareProperties"]["udid"], d[0]["identifier"]) if d else print("")
')
UDID=$(echo "$IDS" | cut -d" " -f1); DEV=$(echo "$IDS" | cut -d" " -f2)
if [ -z "$UDID" ] || [ -z "$DEV" ]; then echo "No encontré tu iPhone. Conéctalo por cable, desbloquéalo y confía en esta Mac."; exit 1; fi

echo "3/4 · Compilando (firmada con tu equipo de Apple)…"
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Debug \
  -destination "platform=iOS,id=$UDID" -derivedDataPath ios/DerivedData -allowProvisioningUpdates build -quiet

echo "4/4 · Instalando y abriendo…"
xcrun devicectl device install app --device "$DEV" ios/DerivedData/Build/Products/Debug-iphoneos/App.app
xcrun devicectl device process launch --device "$DEV" com.blubergames.smush
echo "Listo: SMUSH! está en tu iPhone."
