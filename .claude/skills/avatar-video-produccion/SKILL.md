---
name: avatar-video-produccion
description: >
  Formato DEFINITIVO de producción para videos UGC de avatar (tipo Lara): convierte un
  guion validado en un plan clip por clip de ~10 segundos, y por cada clip entrega DOS
  prompts — ① un PROMPT DE IMAGEN (Método 6C, en inglés) para generar la escena de
  referencia, y ② un PROMPT DE VIDEO (image-to-video, en inglés) que parte de esa imagen
  con acción, microgestos, acento, idioma y el diálogo. Úsalo SIEMPRE que el usuario pida
  "pasar a producción" un guion de avatar, quiera "prompts para grabar los videos", "una
  imagen de referencia y un prompt de video", producir clips de avatar de 10 segundos, o
  crear un video UGC con su avatar desde cero. Va después de la estrategia/guion
  (estratega-avatarhype) y antes de la edición (auto-broll-video). Dispara aunque no se
  nombre "6C" ni "producción": cualquier "dame los prompts para el video del avatar" entra acá.
---

# Producción de video de avatar — formato definitivo

Convierte un guion UGC ya elegido en un **plan de producción clip por clip**. Cada video de
avatar dura **~10 segundos** (una grabación por clip; así trabajan las herramientas de
avatar). El flujo de creación desde cero es:

1. **Estrategia + guion** → skill `estratega-avatarhype` (ángulos, mecanismo, guion).
2. **Producción (esta skill)** → por clip: prompt de imagen (6C) + prompt de video.
3. **Edición** → skill `auto-broll-video` (unir clips, captions palabra-por-palabra,
   transiciones sin fundido, música baja, etc.).

## Reglas globales (no romper)
- **Misma identidad del avatar en TODOS los clips** (mismo avatar/semilla/referencia). Lo que
  cambia clip a clip es **plano + lugar + outfit + acción**, para que se sienta UGC real
  (grabado en distintos días), no un avatar estático.
- **Hook en el primer segundo** (visual + primera frase). El clip 0 suele ir en primerísimo
  primer plano.
- **Un CTA único** al final, con una **palabra clave para comentar** (ej. "IA") que capta leads.
- **Siempre confirmá antes: mercado/idioma y acento del guion.** El diálogo va en el idioma del
  MERCADO (no necesariamente el del usuario). Si no lo dijeron, marcá [suposición].
- Prompts de imagen y video **en inglés**; el **diálogo** en el idioma/acento del mercado.
- Cerrá siempre los prompts con: `No text, no watermark, no distortion.`
- Nunca menciones "AI/CGI/render/hyperrealistic" dentro del prompt de imagen; usá lenguaje de
  realismo iPhone/UGC (ver Método 6C, skill `avatarhype-6c-prompt-engine`).

## Método 6C (orden del prompt de IMAGEN)
Cada prompt de imagen se arma en este orden (una idea por línea):
1. **Cámara/formato** — `Vertical 9:16 iPhone front-camera selfie photo`, plano (extreme
   close-up / medium shot / medium close-up), vibe `casual real UGC`.
2. **Luz** — luz natural de ventana, suave, `slight grain`, mood del lugar.
3. **Personaje (Lara)** — misma identidad en todos los clips; look de creadora real y cercana;
   **piel realista con poros, pecas e imperfecciones**; mirando a cámara.
4. **Ropa** — outfit + accesorios (cambia por clip).
5. **Contexto/lugar** — localización + fondo desenfocado (cambia por clip).
6. **Anclajes** — `No text, no watermark, no distortion.`

## Prompt de VIDEO (Flow / Veo 3, orden)
Generador objetivo: **Google Flow (Veo 3)** con imagen de referencia. Veo SÍ genera cuerpo en
movimiento, gestos y traslados de cámara — hay que **pedírselo explícito**. El error clásico es
pedir "talking-head, subtle motion" → sale una persona sentada, quieta, robótica. NO hacer eso.

1. `Using the reference image as the exact character and setting, generate a realistic vertical video.`
2. **ACCIÓN FÍSICA REAL (lo más importante)** — la persona hace algo con el cuerpo, no solo habla:
   camina un paso / cambia de peso, gesticula con las manos, **se toca el pelo**, se acomoda los
   lentes, agarra y sostiene una taza, señala, se inclina hacia la cámara y vuelve. Ver
   `## MOVIMIENTO REAL` abajo.
3. **Cómo habla**: `talking to the camera like a casual selfie video, handheld feel`.
4. **Movimiento de cámara DENTRO de la toma** (la firma del estilo referencia): la cámara
   **viaja** durante el clip, p.ej. `the camera slowly pushes in from a medium shot to an extreme
   close-up of her face by the end`, o `slow handheld dolly following her as she moves`. No es
   estática.
5. Diálogo con acento: `She says, in <acento> Spanish (casual): "<línea>"`.
6. **Microgestos** anclados a palabras (alza de cejas, parpadeo, media sonrisa, ladeo de cabeza,
   mano que sube, gesto hacia abajo en el CTA).
7. `Realistic skin with pores and subtle imperfections, natural lip-sync, single continuous handheld shot, vertical 9:16, about 8-10 seconds. No text, no watermark, no distortion.`

## MOVIMIENTO REAL (estilo referencia — lo que separa un avatar creíble de uno robot)
Descubrimiento clave (ref: reel `aivideobootcamp` "Big brands are using AI avatars"): lo que hace
que un avatar parezca **persona real** NO es la edición — es que **en la generación** el cuerpo se
mueve y la cámara viaja. Reglas:

- **Una sola Lara** (identidad idéntica en todos los clips vía imagen de referencia). Dos avatares
  interactuando se ve genial pero mantener las dos caras consistentes es lo más difícil de Flow;
  por defecto: **una**.
- **Cada clip = una acción física concreta**, distinta entre clips: `takes a step and leans on the
  kitchen counter`, `tucks a strand of hair behind her ear`, `picks up a coffee mug and holds it`,
  `adjusts her glasses`, `walks slowly across the room`, `points down at the screen`, `leans in
  close like sharing a secret`. Anclá la acción a una palabra del diálogo.
- **La cámara se mueve dentro del clip.** Firma del estilo: arrancar en plano medio y que la cámara
  **entre hasta primerísimo primer plano** de la cara al final (como el FACE/HAIR/TEETH/REAL de la
  referencia). En Flow: `medium shot, the camera slowly and smoothly pushes in to an extreme
  close-up by the end`.
- **Respaldo en edición (garantía):** Flow tiene varianza — a veces el traslado de cámara sale
  débil. No pasa nada: ese viaje **medio → primer plano** lo puedo **garantizar en edición** con un
  push-in suave sobre cualquier clip. Así: Flow aporta el **movimiento del cuerpo** (que sólo se
  genera), y la **edición** asegura el **movimiento de cámara**. Si un clip sale demasiado quieto de
  cuerpo, ese clip se regenera (no se arregla en post).

## Efectos de cámara (catálogo)
Se decide por clip, en DOS capas. En **generación**: acción del cuerpo + un traslado de cámara.
Los acentos potentes y sincronizados a la palabra van en **edición**.

- **Generación (dentro del prompt ②, inglés):** `slow push-in from medium to close-up`,
  `handheld dolly following her`, `slight orbit`, `slow pull-out revealing the room`.
- **Edición (post, HyperFrames — skill `auto-broll-video` + `hyperframes-keyframes`):**
  push-in garantizado medio→primer plano, punch-in/zoom en la palabra clave, `snap zoom` en el CTA,
  `shake` corto en el hook, Ken Burns, speed ramp, whip-pan / zoom-through entre clips.

## FORMATO DE SALIDA (obligatorio, por clip)

```
CLIP N · [función] (~10s) — plano: [primerísimo primer plano / plano medio / medio-corto]

① PROMPT IMAGEN
```txt
<prompt 6C en inglés>
```

② PROMPT VIDEO
```txt
<prompt image-to-video en inglés, con el diálogo dentro>
```

Diálogo: "<línea en el idioma/acento del mercado>"
Acción física: <qué hace con el cuerpo, anclado a una palabra — camina/agarra/se toca el pelo/señala>
Microgestos: <alza de cejas, parpadeo, media sonrisa, ladeo de cabeza>
Acento / idioma: <ej. español rioplatense (Argentina)>
③ Cámara — generación: <traslado, ej. push-in de medio a primer plano> · edición: <acento, ej. punch-in en "<palabra>">
```

Al final del guion agregá:
- **MONTAJE**: unir los clips con disolvencia suave (0.3–0.4s) o corte limpio; subtítulos
  palabra por palabra (bold, fondo negro semi, palabra activa en color); música de fondo baja
  (~15%); la cara siempre visible. (La edición la ejecuta `auto-broll-video`.)
- **ESTILO DE EDICIÓN (avatar ads) — SIN imágenes sobrepuestas**: en estos anuncios de avatar
  NO se agrega B-roll ni ilustraciones encima. El dinamismo lo dan **efectos de cámara** sobre
  el propio clip: **zoom-in / punch-in** en la palabra clave, **zoom-out / pull-out** para
  revelar, **snap-zoom** rápido en el CTA y en acentos, y **whip / zoom-through** como transición
  entre clips. Los zooms se sincronizan a la palabra exacta.
  DIVISIÓN DE TAREAS: el **movimiento del cuerpo** (caminar, tocarse el pelo, gesticular) SÓLO se
  logra en la **generación** (Flow) — no se puede agregar en post. El **movimiento de cámara**
  (push-in medio→primer plano, punch, snap) se **garantiza en edición** aunque Flow no lo haya
  aplicado. Truco extra: para simular **cambio de plano** dentro de un clip, cortá el mismo clip en
  dos encuadres (ancho → recorte más cerrado) — un punch-cut que parece multicámara.
- **VELOCIDAD (importante)**: los clips generados por IA salen lentos/arrastrados. Aceleralos
  siempre **~1.15x** (rango 1.1–1.25x) con **pitch preservado** para que quede dinámico y la voz
  no suene de ardilla. ffmpeg: video `setpts=PTS/1.15`, audio `atempo=1.15` (atempo mantiene el
  tono hasta 2x). En hooks se puede ir a 1.2x; en el CTA un poco menos. Reajustá los tiempos de
  captions/efectos DESPUÉS de acelerar.
- **POR QUÉ CONVIERTE**: 1-2 frases (ángulo / mecanismo / gatillo).

## Ejemplo montado (1 clip)
```
CLIP 0 · HOOK (~10s) — plano: primerísimo primer plano

① PROMPT IMAGEN
```txt
Vertical 9:16 iPhone front-camera selfie photo, extreme close-up of the face almost filling the frame, casual real UGC vibe.
Soft natural window light from the side, gentle shadows, slight grain, cozy home mood.
Lara — a relatable female content creator in her late 20s, natural attractive real-creator look, visible realistic skin detail with pores, freckles and subtle imperfections, looking straight into the camera.
Wearing a simple cream knit sweater.
Cozy living room, blurred bookshelf and warm lamp in the background.
No text, no watermark, no distortion.
```

② PROMPT VIDEO
```txt
Using the reference image as the exact character and setting, generate a realistic vertical selfie video.
The same woman holds her phone at arm's length and talks to the camera like a casual selfie video, handheld feel. She is physically active: she raises her free hand into frame with an open "stop" gesture on "pará", then tucks a loose strand of hair behind her ear, and leans in closer to the lens as if sharing a secret.
Camera: starts as a medium close-up and the camera slowly and smoothly pushes in to an extreme close-up of her face by the end.
She says, in Argentine Rioplatense Spanish (casual, like a voice note to a friend): "Pará dos segundos. Todo lo que estás viendo ahora mismo no es real. Yo no existo: soy un avatar hecho con inteligencia artificial."
Micro-gestures: small eyebrow raise on "no es real"; one natural blink and a subtle knowing half-smile at the end.
Realistic skin with pores and subtle imperfections, natural lip-sync, single continuous handheld shot, vertical 9:16, about 8-10 seconds. No text, no watermark, no distortion.
```

Diálogo: "Pará dos segundos. Todo lo que estás viendo ahora mismo no es real. Yo no existo: soy un avatar hecho con inteligencia artificial."
Acción física: mano abierta de "pará" → se acomoda el pelo → se acerca al lente.
Microgestos: alza de cejas en "no es real"; parpadeo + media sonrisa al final.
Acento / idioma: español rioplatense (Argentina).
③ Cámara — generación: push-in de medio a primer plano · edición: punch-in en "no es real".
```
