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

## Prompt de VIDEO (image-to-video, orden)
1. `Image-to-video from the reference image, keep her exact identity and setting.`
2. Acción principal + cómo habla (tono), `handheld selfie feel, subtle natural motion`.
3. Diálogo con acento: `She says, in <acento> Spanish (casual): "<línea>"`.
4. **Microgestos** concretos anclados a palabras (alza de cejas, parpadeo, media sonrisa,
   ladeo de cabeza, mano que sube, guiño, gesto hacia abajo en el CTA).
5. `Realistic lip-sync, single continuous shot, vertical 9:16, about 10 seconds. No text, no watermark, no distortion.`

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
Acción + microgestos: <qué hace, anclado a palabras>
Acento / idioma: <ej. español rioplatense (Argentina)>
```

Al final del guion agregá:
- **MONTAJE**: unir los clips con disolvencia suave (0.3–0.4s) o corte limpio; subtítulos
  palabra por palabra (bold, fondo negro semi, palabra activa en color); música de fondo baja
  (~15%); la cara siempre visible. (La edición la ejecuta `auto-broll-video`.)
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
Image-to-video from the reference image, keep her exact identity and setting.
The same woman talks straight to the camera in a close, confidential tone, handheld selfie feel, subtle natural motion.
She says, in Argentine Rioplatense Spanish (casual, like a voice note to a friend): "Pará dos segundos. Todo lo que estás viendo ahora mismo no es real. Yo no existo: soy un avatar hecho con inteligencia artificial."
Micro-gestures: leans slightly toward the camera on "pará"; a small eyebrow raise on "no es real"; one natural blink and a subtle knowing half-smile at the end.
Realistic lip-sync, single continuous shot, vertical 9:16, about 10 seconds. No text, no watermark, no distortion.
```

Diálogo: "Pará dos segundos. Todo lo que estás viendo ahora mismo no es real. Yo no existo: soy un avatar hecho con inteligencia artificial."
Acción + microgestos: se acerca en "pará"; alza de cejas en "no es real"; parpadeo + media sonrisa al final.
Acento / idioma: español rioplatense (Argentina).
```
