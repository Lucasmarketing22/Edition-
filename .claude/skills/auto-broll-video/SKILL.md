---
name: auto-broll-video
description: >
  Edita automáticamente un video de avatar / talking-head / UGC agregándole B-roll de
  imágenes generadas con IA (estilo stickman moderno u otro), sincronizadas a la palabra
  clave, con transiciones variadas, efectos de sonido, música de fondo y fundido a negro —
  todo armado en HyperFrames y renderizado a MP4. Úsalo SIEMPRE que el usuario suba o
  mencione un video suyo (mp4/mov) y pida "editarlo", "agregarle imágenes IA", "ponerle
  B-roll", "hacerlo más dinámico", "estilo página de ventas / VSL", "que aparezcan dibujos
  cuando hablo", agregar música o efectos de sonido a su video, o convertir su intro/avatar
  en un video con ilustraciones. Cubre también captions palabra-por-palabra si hay acceso a
  transcripción. Dispara aunque el usuario no diga "HyperFrames" ni "B-roll" explícitamente:
  cualquier "editame este video" sobre footage de una persona hablando entra acá.
---

# Auto B-roll Video Editor

Convierte el video de una persona hablando (avatar IA, UGC, talking-head) en un video
dinámico estilo VSL: **el avatar es protagonista y sigue hablando**, y en la palabra clave
de cada frase **aparece una imagen (B-roll) unos ~2s con animación + sonido y se va**.
Se arma como composición HyperFrames y se renderiza a MP4 vertical.

Este skill captura un flujo ya probado end-to-end. Seguí los pasos en orden; cada uno tiene
su script o su patrón. Las decisiones marcadas como **⚠ Lección** evitan errores concretos
que ya costaron iteraciones.

## Cuándo NO usar
- Video sin persona hablando / música pura → `/music-to-video`.
- Solo captions/subtítulos sobre footage sin B-roll → `/embedded-captions`.
- Explainer sin footage (todo inventado) → `/faceless-explainer`.

## Requisitos del entorno
- **ffmpeg + ffprobe** en PATH (`sudo apt-get install -y ffmpeg`).
- **HyperFrames CLI** (`npx hyperframes@latest`) y su Chrome (`npx hyperframes browser ensure`).
- **Red (egress)**: en Claude Code on the web el entorno debe permitir `api.kie.ai`,
  `*.kie.ai`, `file.aiquickdraw.com`, `*.aiquickdraw.com` (Network access = Custom o Full).
  Para **captions** (transcripción) hay que sumar `api.openai.com` (Whisper) **o**
  `huggingface.co` + `*.hf.co` (Whisper local). Sin ese dominio, los captions no se pueden
  generar acá.
- **API key de kie.ai** (imágenes Nano Banana y música Suno), pasada por variable de entorno.
  Guardala en el scratchpad (fuera del repo), NUNCA la commitees. Avisá al usuario de
  regenerar sus keys al terminar si las pegó en el chat.

## Flujo (8 pasos)

### 1. Preparar el video base
- `ffprobe` para leer codec, resolución, fps, duración.
- **⚠ Lección — transcodificar a H.264.** Si el codec es HEVC/H.265, Chromium no lo decodifica
  bien en el render. Convertí siempre a H.264:
  `ffmpeg -y -i IN.mov -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k assets/base.mp4`
- Extraé el audio para el paso 2: `ffmpeg -y -i IN -vn -ac 1 -ar 16000 -c:a libmp3lame -q:a 4 assets/audio.mp3`
- La resolución del canvas = la del video (ej. 1080x1908). Mirá un frame del video
  (`ffmpeg -ss 5 -i base.mp4 -frames:v 1 f.png`) para saber dónde queda la cara.

### 2. Timing de las frases (sin ASR)
Necesitás saber en qué segundo cae cada frase para poner cada imagen en su momento.
Corré `scripts/detect_beats.py assets/audio.mp3` → devuelve los segmentos de habla
(entre pausas) usando `ffmpeg silencedetect`. Normalmente hay 1 segmento por frase.
Mapeá cada concepto/imagen al punto medio de su frase. No necesita transcripción.

### 3. Diseñar las imágenes desde el guion
Pedile al usuario el **texto del video** (o transcribilo si hay acceso — ver Captions).
Elegí 5–7 conceptos clave (uno por frase importante) y escribí un prompt visual por cada uno.
Escribí un `scenes.json` (ver `scripts/generate_images.py` para el formato) con:
- `style`: bloque de estilo compartido — **el MISMO personaje en todas** para consistencia.
  Estilo por defecto que funcionó: *stickman moderno "faceless YouTube": monigote blanco,
  cara expresiva de ojos grandes, buzo de color (rojo), contornos negros limpios, vector
  plano, líneas de movimiento, fondo claro.* (Preguntá/confirmá el estilo con el usuario;
  otros: sticker cartoon, flat vector, 3D/clay, hecho a mano a color.)
- `no_text_rule`: **⚠ Lección** — Nano Banana tiende a escribir texto en inglés dentro de la
  imagen. Prohibí texto explícitamente ("no text, words, letters, numbers"), salvo una
  palabra intencional (ej. la del CTA) marcando esa escena con `keep_text: true`.
- `aspect_ratio`: `"9:16"` para vertical full-screen.

### 4. Generar las imágenes (en paralelo)
`KIE_API_KEY=... python3 scripts/generate_images.py scenes.json --out avatar_images/`
Genera todas en paralelo (createTask) y descarga secuencial (evita el 403 de Cloudflare).
**⚠ Lección** — la descarga necesita `User-Agent` de navegador o Cloudflare la bloquea (403).
Revisá cada imagen; si alguna tiene texto no deseado, regenerá solo esa:
`python3 scripts/generate_images.py scenes.json --out avatar_images/ --only 2`
**⚠ Costo**: cada imagen gasta créditos de kie. Si sale 402 "Credits insufficient", avisá al
usuario que cargue créditos; dejá esa imagen pendiente y seguí con el resto.

### 5. Música de fondo (opcional)
`KIE_API_KEY=... python3 scripts/generate_music.py --mood "calm soft piano underscore" --seconds 22.4 --out assets/music/bgm.mp3`
Genera con Suno (kie.ai), recorta a la duración del video con fade-in/out. Se mezcla al
**~15–20%** bajo la voz. **⚠ Lección** — el endpoint de Suno (`/api/v1/generate`) EXIGE
`callBackUrl`; el script pasa uno dummy y hace polling en `/api/v1/generate/record-info`.

### 6. Efectos de sonido
Copiá SFX del skill `media-use` (ya vienen en el repo):
`cp .claude/skills/media-use/audio/assets/sfx/{pop,whoosh-short,whoosh,whoosh-cinematic,sparkle,chime}.mp3 assets/sfx/`
Asigná un SFX distinto por transición, todos al **mismo volumen bajo (~0.15)** — el usuario
valora la variedad y que no sea invasivo.

### 7. Armar la composición HyperFrames
Partí de `assets/composition.template.html` (cópiala a `index.html` del proyecto). Es una
composición standalone 1080x<alto>, con:
- `<video>` base (avatar, visible siempre) + `<audio>` de la voz + `<audio>` de música (0.15).
- Un `<img class="shot clip">` por imagen, con `data-start`/`data-duration` = ventana del
  insert (~2s en el momento de la frase, del paso 2).
- Un `<audio>` de SFX por insert (volumen 0.15), en el `data-start` del insert.
- Overlay de marca (fade-in a los 2s) + `#fadeout` a negro (0.5s) al final.
- GSAP vendorizado local (`vendor/gsap.min.js`) — bajalo una vez con curl; **⚠ Lección**: el
  CDN puede colgar el navegador del render (timeout de navegación).

**⚠ LECCIÓN CLAVE — transiciones SIN fundido de opacidad.** Cada insert debe entrar y salir
**solo con movimiento** (escala desde 0, slide desde fuera de cuadro, flip 3D, etc.) a
**opacidad 100%**. NO uses `autoAlpha`/opacity para el crossfade: como las ilustraciones
tienen fondo claro, al pasar por opacidad parcial "lavan"/difuminan la cara del avatar y se
ve como si se desenfocara y reenfocara en cada imagen. Con movimiento puro, el avatar nunca
queda tapado a medias → siempre nítido. Usá transiciones variadas (pop, slide izq, slide der,
flip 3D, subir, spin) para dinamismo. Ver el `<script>` del template.

Validá: `npx hyperframes check` (0 errores). Sacá snapshots en los picos de entrada y en
las salidas para eyeballear: `npx hyperframes snapshot --at 1.9,6.6,10.86,...` y mirá el
contact-sheet (confirmá que en las salidas el avatar se ve nítido, sin lavado).

### 8. Render final en alta calidad
**⚠ Lección** — el render "standard" comprime feo. Usá calidad alta:
`npx hyperframes render --quality high --crf 16 --output out/final.mp4`
1080p vertical con bitrate alto es el punto justo para Reels/TikTok/Shorts (las redes
recomprimen a 1080p igual). Entregá el MP4 con `SendUserFile`. Avisá al usuario de subir el
archivo original directo a la app, no una copia reenviada por chat (se recomprime).

## Captions palabra-por-palabra (si hay acceso a transcripción)
El usuario suele quererlos: abajo, bold grande, fondo negro semitransparente, **palabra
activa resaltada en cyan** (karaoke). Requiere timing por palabra:
- Con `api.openai.com` permitido: OpenAI Whisper (`whisper-1`, `response_format=verbose_json`,
  `timestamp_granularities[]=word`) → timing exacto por palabra.
- Con `huggingface.co` permitido: `faster-whisper` local (gratis, offline tras bajar el modelo).
- Sin ninguno: pedí el texto y usá alineación forzada offline (`aeneas`: espeak + ffmpeg,
  sin modelos externos) para el timing por frase/palabra.
Muchos usuarios prefieren ponerlos ellos mismos en su editor — preguntá antes de armarlos.

## Notas de seguridad
- Guardá las API keys en el scratchpad (permiso 600), nunca en el repo. Agregá `*.env`,
  `secrets*`, media (`*.mp4 *.png *.mp3`) al `.gitignore` del proyecto.
- Al terminar, recordale al usuario **regenerar** las keys que haya pegado en el chat.

## Archivos del skill
- `scripts/generate_images.py` — genera imágenes IA (Nano Banana / kie.ai) desde `scenes.json`.
- `scripts/generate_music.py` — genera música (Suno / kie.ai), recorta con fades.
- `scripts/detect_beats.py` — segmentos de habla vía `ffmpeg silencedetect`.
- `assets/composition.template.html` — plantilla de la composición HyperFrames (transiciones
  sin-fundido, música, SFX, overlay, fade). Copiala a `index.html` y adaptá shot list + timings.
