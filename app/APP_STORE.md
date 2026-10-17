# SMUSH!: textos para la App Store

Para copiar y pegar en App Store Connect. El idioma principal es inglés; el español se agrega como localización (**App Store → +** junto al idioma → **Spanish (Mexico)**).

| Dato | Valor |
|---|---|
| Bundle ID | `com.blubergames.smush` |
| Dispositivos | iPhone (vertical) y iPad (horizontal) |
| Primer build | 1.0 (2), subido el 17 oct 2026 con `app/release.sh` |
| Encriptación | No usa (ya está declarado en el `Info.plist`) |

## App Information

| Campo | Qué poner |
|---|---|
| **Name** | `SMUSH! Cozy Alien Clicker` (o el que pusiste al crear la app; máx. 30) |
| **Subtitle** (EN) | `A calm, satisfying clicker` |
| **Subtitle** (ES) | `Un clicker para relajarte` |
| **Category** | Primary: **Games → Casual** · Secondary: **Games → Simulation** |
| **Content Rights** | "No, it does not contain, show, or access third-party content" |
| **Privacy Policy URL** | `https://blubergames.com/privacy/` |

## Age Rating
Todo **None / No**, menos **Cartoon or Fantasy Violence → Infrequent/Mild** (los marcianitos se aplastan, se electrocutan y se los lleva una ola, todo caricaturesco y sin sangre). Con eso Apple probablemente le pone **9+**. Si prefieres 4+, contesta None también ahí, pero es más honesto marcarlo como leve.

No tiene compras, anuncios, chat, cuentas ni navegador web.

## App Privacy
**"No, we do not collect data from this app"**. El juego no tiene cuentas, analítica ni anuncios; el avance se guarda solo en el dispositivo.

## Pricing and Availability
Free, todos los países.

---

## Inglés (English U.S.)

**Promotional Text** (170)
```
Squish wave after wave of aliens, unlock powerful tools, hire helpers that work while you're away and travel across six islands. No ads, no account.
```

**Keywords** (100)
```
clicker,idle,tap,relaxing,casual,incremental,smash,cozy,offline,tapper,calm,satisfying,zen,asmr
```

**Description**
```
Aliens keep wandering onto your screen. Tap to squish them, collect their coins and unwind, one island at a time.

SMUSH! is a relaxing clicker made for quick breaks and long, calm sessions alike. Every tap feels soft and satisfying, the music is gentle, and there's always something new to unlock.

SQUISH, COLLECT, UPGRADE
• Tap the aliens before they sneak away
• Unlock new tools: Shock, Saw, Bombs, Tsunami, Meteors, Avalanche, Car, Arrows and a Toy Train
• Make every tap bigger and every alien worth more

HIRE HELPERS
• Electric clouds and hunting fingers smush aliens for you
• They keep working while you're away, so there's always a reward waiting

TRAVEL TO SIX ISLANDS
• The Void, The Beach, The Slopes, The City, The Jungle and The Playroom
• Each island has its own look, music, alien costumes, special event and signature tool

ALWAYS SOMETHING TO DO
• Missions that pay out automatically
• 68 trophies to unlock and collectibles to find on every island
• Catch the rare King alien, build combos and pop coin bubbles

MADE TO FEEL GOOD
• Soft sounds and gentle haptics
• Light and dark themes
• English and Spanish
• Plays on iPhone and on iPad in landscape
• No ads and no account: your progress stays on your device

Made with care by BluBer Games, an independent studio of calm games.
```

---

## Español (Spanish Mexico)

**Promotional Text** (170)
```
Aplasta oleadas de marcianos, desbloquea herramientas poderosas, contrata ayudantes que trabajan mientras no estás y viaja por seis islas. Sin anuncios ni cuentas.
```

**Keywords** (100)
```
clicker,idle,marcianos,aliens,tocar,aplastar,relajante,casual,incremental,zen,offline,calma
```

**Description**
```
Los marcianos no dejan de entrar a tu pantalla. Tócalos para aplastarlos, junta sus monedas y relájate, una isla a la vez.

SMUSH! es un clicker relajante, hecho tanto para un ratito como para sesiones largas y tranquilas. Cada toque se siente suave y satisfactorio, la música es tranquila y siempre hay algo nuevo por desbloquear.

APLASTA, JUNTA, MEJORA
• Toca a los marcianos antes de que se escapen
• Desbloquea herramientas: Descarga, Sierra, Bombas, Tsunami, Meteoritos, Avalancha, Carro, Flechas y un Tren de juguete
• Haz tus toques más grandes y que cada marciano valga más

CONTRATA AYUDANTES
• Nubes eléctricas y dedos cazadores aplastan marcianos por ti
• Siguen trabajando mientras no estás: siempre hay una recompensa esperándote

VIAJA POR SEIS ISLAS
• The Void, The Beach, The Slopes, The City, The Jungle y The Playroom
• Cada isla tiene su propio paisaje, música, disfraces, evento especial y herramienta

SIEMPRE HAY ALGO QUE HACER
• Misiones que se cobran solas
• 68 trofeos y coleccionables en cada isla
• Atrapa al Rey, arma combos y revienta burbujas de monedas

HECHO PARA SENTIRSE BIEN
• Sonidos suaves y vibración ligera
• Tema claro y oscuro
• Inglés y español
• En iPhone y en iPad en horizontal
• Sin anuncios ni cuentas: tu avance se queda en tu dispositivo

Hecho con cariño por BluBer Games, un estudio independiente de juegos tranquilos.
```

---

## Versión 1.0

| Campo | Qué poner |
|---|---|
| **Support URL** | `https://blubergames.com/support/` |
| **Marketing URL** | `https://blubergames.com` |
| **Copyright** | `2026 BluBer Games` |
| **Build** | 1.0 (2) |
| **Sign-In required** | No |

**Notes for App Review**
```
SMUSH! is a relaxing single-player clicker. No account, sign-in, purchases or network features are needed: just tap the aliens on the field to squish them and spend the coins in the Shop. Progress is saved locally on the device. On iPad the game is played in landscape.
```

---

## Imágenes (Previews and Screenshots)
Se generan con `store/shots.js` (capturas del juego en Chrome sin ventana) y `store/make_store.py` (título, marco y fondo). Salen en `store/appstore/`, en inglés (`en/`) y español (`es/`); en la ficha en español usa las de `es/`. Súbelas en orden (1 a 6).

| Pestaña en App Store Connect | Carpeta | Tamaño |
|---|---|---|
| iPhone 6.9" | `store/appstore/iphone-6.9/` | 1320 × 2868 |
| iPhone 6.3" | `store/appstore/iphone-6.3/` | 1206 × 2622 |
| iPad 13" | `store/appstore/ipad-13/` | 2752 × 2064 (horizontal) |
| Header | `store/appstore/creatives/header-3840x1646-<idioma>.png` | 3840 × 1646 |
| Search Results | `store/appstore/creatives/search-3840x2560-<idioma>.png` | 3840 × 2560 |

Header y Search Results llevan lo importante (ícono, logo y frase) dentro de la zona segura de Apple. No uses el formato universal de 5244 × 2950: Apple lo recorta muchísimo.
