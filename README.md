# 🐾 Gacha Zoo

> Una máquina gachapon 3D voxel llena de animalitos coleccionables. ¡Tira de la palanca y a ver qué cae! 🎰

Juego web de "gacha" hecho en **un único `index.html`** con Three.js: tiras cápsulas, coleccionas criaturas voxel de varias series, las cuidas en tu Jardín y compites en minijuegos. Incluye un modo JRPG (el Dojo), hucha clicker y guardado en la nube con cuentas familiares.

## ✨ Características

- 🧊 Criaturas 3D voxel modeladas por código, repartidas en múltiples series.
- 🎰 Máquina gachapon con cápsulas de distintas rarezas (común, raro, épico, lego).
- 🕹️ Varios minijuegos y un modo JRPG (el Dojo, con cinturones y duelos).
- 🌱 El Jardín para cuidar y exhibir tu colección + hucha clicker.
- 👨‍👩‍👧 Cuentas con PIN y familias: cloud save, intercambios y rankings entre miembros.
- 🎵 Banda sonora propia por serie, generada desde MIDI con SoundFont.
- 📱 PWA instalable (manifest + service worker), pensada para móvil.

## 🚀 Cómo ejecutar

Es un juego web estático: basta servir la carpeta y abrir `index.html`.

```bash
# servidor local (la fuente, no el build)
python3 -m http.server 8431
# luego abre http://127.0.0.1:8431/index.html
```

Atajos útiles vía el `Makefile`:

```bash
make serve     # levanta el servidor local
make check     # valida la sintaxis del JS embebido y del worker
make help      # lista todos los comandos
```

### Parámetros de depuración (querystring)

| Parámetro | Efecto |
|---|---|
| `?demo=1` | Desbloquea la colección de la serie actual |
| `?s=N` | Fuerza una serie concreta (0-indexada) |
| `?garden=1` | Entra directamente al Jardín |
| `?dojo=1` | Abre el panel del Dojo |

### Regenerar la música de una serie

```bash
make music SID=s14 PROGS=24,46,33   # programas GM por canal: melodía, acomp., bajo
```

## 🎮 Controles

- 🖱️ **Ratón / toque**: tirar de la palanca, abrir cápsulas y navegar los menús.
- 👆 Interfaz táctil pensada para jugar en el móvil en vertical.

## 🛠️ Tecnología

- **Three.js r160** (vía importmap + CDN jsdelivr) para el 3D voxel.
- HTML + CSS + un `<script type="module">` — todo el juego vive en `index.html`.
- **Cloudflare Pages** + un Worker (`worker-src.js` → `_worker.js`) con base de datos **D1** para cuentas, cloud save y multijugador.
- Música compuesta en Python (MIDI maestro en `src-music/`) y renderizada con fluidsynth + SoundFont a `.m4a`.
- PWA: `manifest.json` + `sw.js`.

> Nota: varias series son fan-art de IP ajena hecho para uso personal/familiar. El despliegue lleva `noindex` y no hay monetización.

## 📦 Proyecto personal

Proyecto personal y familiar hecho por diversión. ¡Feliz colección! 🐣
