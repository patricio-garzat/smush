"""Arma la carpeta www/ de la app de iOS a partir del juego web (../index.html y ../audio/).

El juego vive en UN solo archivo (../index.html): lo que cambies ahí sale igual en la web y en la app.
Diferencias de la app:
- Se quitan los íconos web (en la app no sirven).
- Sin zoom de ninguna forma (pellizco ni doble toque).
- La versión que se ve en Ajustes es la de la app (la del proyecto de Xcode), con la del juego entre paréntesis.

Uso: python3 build-www.py   (o npm run build, que además copia www/ al proyecto de Xcode)
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
WWW = os.path.join(HERE, "www")

html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

# Cosas solo de la web
for tag in (
    '<link rel="icon" type="image/svg+xml" href="brand/favicon.svg">\n',
    '<link rel="icon" type="image/png" sizes="32x32" href="brand/favicon-32.png">\n',
    '<link rel="icon" type="image/png" sizes="192x192" href="brand/favicon-192.png">\n',
    '<link rel="apple-touch-icon" href="brand/apple-touch-icon.png">\n',
):
    assert tag in html, tag
    html = html.replace(tag, "")

# Sin zoom en la app: ni pellizco ni doble toque
vp = re.search(r'<meta name="viewport" content="[^"]*">', html)
assert vp, "no encontré el viewport"
html = html.replace(vp.group(0), '<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">')
no_zoom = """<style>html, body { touch-action: manipulation; -webkit-text-size-adjust: 100%; }</style>
<script>
  // Bloquea el pellizco (gestos de WebKit) y el doble toque para hacer zoom
  ["gesturestart", "gesturechange", "gestureend"].forEach((ev) => document.addEventListener(ev, (e) => e.preventDefault(), { passive: false }));
  document.addEventListener("touchmove", (e) => { if (e.touches.length > 1) e.preventDefault(); }, { passive: false });
</script>
"""
html = html.replace("</head>", no_zoom + "</head>", 1)

# Versión de la app (Ajustes → Versión): la del proyecto de Xcode, y la del juego entre paréntesis
pbx = open(os.path.join(HERE, "ios", "App", "App.xcodeproj", "project.pbxproj"), encoding="utf-8").read()
version = re.search(r"MARKETING_VERSION = ([0-9.]+);", pbx).group(1)
build = re.search(r"CURRENT_PROJECT_VERSION = (\d+);", pbx).group(1)
m = re.search(r'const VERSION = "([^"]+)";', html)
assert m, "no encontré la versión del juego"
game = m.group(1)
html = html.replace(m.group(0), f'const VERSION = "{version} ({build}) · {game}";', 1)

shutil.rmtree(WWW, ignore_errors=True)
os.makedirs(WWW)
shutil.copytree(os.path.join(ROOT, "audio"), os.path.join(WWW, "audio"))
open(os.path.join(WWW, "index.html"), "w", encoding="utf-8").write(html)
print("www/ listo:", len(html) // 1024, "KB · app", version, f"({build}) · juego {game}")
