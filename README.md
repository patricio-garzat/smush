# SMUSH! · BluBer Games

El segundo juego de **BluBer Games**: un clicker tranquilo y satisfactorio para iOS y la web. Aplasta marcianitos, gana monedas, contrata dedos ayudantes y desbloquea herramientas.

## Estructura

| Ruta | Qué es |
|---|---|
| `index.html` | El juego web completo, en un solo archivo |
| `CLAUDE.md` | Notas del juego para Claude: identidad, estado y balance |
| `brand/` | Ícono, logo y personajes (`marcianitos.svg`) |
| `store/` | Capturas e imágenes para la App Store |

`app/` es la app de iOS (Capacitor). Toma el juego de `index.html`, así que los cambios salen igual en la web y en la app. Para probarla en tu iPhone: `app/run-on-iphone.sh`.

## Probarlo
Abre `index.html` en el navegador, o sírvelo con `python3 -m http.server` y entra desde el iPhone en la misma red.

## Enlaces
- **Estudio:** https://blubergames.com
- **Guía de marca:** [`../blubergames-site/BRAND.md`](../blubergames-site/BRAND.md)
