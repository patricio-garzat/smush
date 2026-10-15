#!/bin/bash
# Instala SMUSH! en tu iPhone para probarlo (no sube nada a la App Store).
# Toma el juego de ../index.html (el mismo de la web), arma la app, la compila firmada con tu equipo y la abre.
# Uso: ./run-on-iphone.sh     (con el iPhone conectado por cable, desbloqueado y con Modo de desarrollador)
set -e
cd "$(dirname "$0")"

echo "1/4 · Armando la app con el juego de la web…"
npm run build --silent

echo "2/4 · Buscando tu iPhone…"
UDID=$(xcrun xctrace list devices 2>/dev/null | grep -E "iPhone|iPad" | grep -v Simulator | grep -oE "\(([0-9A-F]{8}-[0-9A-F]{16})\)" | head -1 | tr -d "()")
DEV=$(xcrun devicectl list devices 2>/dev/null | grep -E "iPhone|iPad" | grep -oE "[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}" | head -1)
if [ -z "$UDID" ] || [ -z "$DEV" ]; then echo "No encontré tu iPhone. Conéctalo por cable, desbloquéalo y confía en esta Mac."; exit 1; fi

echo "3/4 · Compilando (firmada con tu equipo de Apple)…"
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Debug \
  -destination "platform=iOS,id=$UDID" -derivedDataPath ios/DerivedData -allowProvisioningUpdates build -quiet

echo "4/4 · Instalando y abriendo…"
xcrun devicectl device install app --device "$DEV" ios/DerivedData/Build/Products/Debug-iphoneos/App.app
xcrun devicectl device process launch --device "$DEV" com.blubergames.smush
echo "Listo: SMUSH! está en tu iPhone."
