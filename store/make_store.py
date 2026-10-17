"""Imágenes de la App Store de SMUSH!: capturas con título (iPhone 6.9", 6.3" y iPad 13") y las portadas
Header (3840 x 1646) y Search Results (3840 x 2560), en inglés y español.

1. node --experimental-websocket store/shots.js phone en   (y phone es, ipad en, ipad es) → store/raw/
2. python3 store/make_store.py                                → store/appstore/…
Necesita el servidor local en :8791 (la carpeta BluBer Games). Todo se dibuja en compose.html con Chrome
sin ventana a 2× y sale del tamaño exacto que pide Apple, sin transparencia.
"""
import os
import subprocess
import urllib.parse

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "appstore")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "http://localhost:8791/Smush/store/compose.html"

SIZES = {"iphone-6.9": ("phone", 1320, 2868), "iphone-6.3": ("phone", 1206, 2622), "ipad-13": ("ipad", 2752, 2064)}
SCENES = ["squish", "train", "helpers", "levels", "trophies", "city"]
TEXT = {
    "en": {
        "squish": ("<b>Squish</b> every<br>last alien", "A relaxing clicker for any moment"),
        "train": ("Unlock <b>powerful</b><br>tools", "Saws, meteors, a tsunami and more"),
        "helpers": ("Hire <b>helpers</b>", "They keep working while you're away"),
        "levels": ("Travel to<br><b>six islands</b>", "Each with its own music and style"),
        "trophies": ("<b>68 trophies</b><br>to unlock", "Plus missions, collectibles and rare finds"),
        "city": ("Calm, <b>day</b><br>or <b>night</b>", "Light and dark themes"),
        "header": "Squish. Collect. Relax.",
        "search": "A calm, satisfying clicker",
    },
    "es": {
        "squish": ("<b>Aplasta</b><br>a todos", "Un clicker relajante para cualquier momento"),
        "train": ("Herramientas<br><b>poderosas</b>", "Sierras, meteoritos, un tsunami y más"),
        "helpers": ("Contrata<br><b>ayudantes</b>", "Siguen trabajando mientras no estás"),
        "levels": ("Viaja por<br><b>seis islas</b>", "Cada una con su propia música y estilo"),
        "trophies": ("<b>68 trofeos</b><br>por ganar", "Además de misiones, coleccionables y sorpresas"),
        "city": ("Tranquilo, de<br><b>día</b> o de <b>noche</b>", "Tema claro y oscuro"),
        "header": "Aplasta. Junta. Relájate.",
        "search": "Un clicker tranquilo y satisfactorio",
    },
}


def shoot(params, w, h, out):
    """Abre compose.html a w/2 x h/2 px con 2× y guarda la foto de w x h, sin transparencia."""
    url = BASE + "?" + urllib.parse.urlencode({**params, "w": w // 2, "h": h // 2})
    tmp = out + ".tmp.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w // 2},{h // 2}",
                    "--force-device-scale-factor=2", "--virtual-time-budget=4000", f"--screenshot={tmp}", url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(tmp).convert("RGB")
    assert im.size == (w, h), (out, im.size)
    im.save(out, optimize=True)
    os.remove(tmp)
    print(os.path.relpath(out, HERE), im.size)


for lang, T in TEXT.items():
    for folder, (dev, w, h) in SIZES.items():
        d = os.path.join(OUT, folder, lang)
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(SCENES, 1):
            cap, sub = T[s]
            shoot({"kind": "shot", "dev": dev, "img": f"raw/{dev}-{lang}-{s}.png", "cap": cap, "sub": sub}, w, h, os.path.join(d, f"{i}-{s}.png"))
    d = os.path.join(OUT, "creatives")
    os.makedirs(d, exist_ok=True)
    # Zonas seguras de Apple (en px de la imagen final; compose.html trabaja a la mitad)
    shoot({"kind": "header", "safe": "548,246,823,330", "tag": T["header"]}, 3840, 1646, os.path.join(d, f"header-3840x1646-{lang}.png"))
    shoot({"kind": "search", "safe": "418,382,1084,515", "tag": T["search"]}, 3840, 2560, os.path.join(d, f"search-3840x2560-{lang}.png"))
