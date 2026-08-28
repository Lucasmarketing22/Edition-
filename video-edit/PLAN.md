# Video edit — plan y estado (handoff)

Proyecto: editar el intro del usuario (avatar/UGC) agregando **imágenes IA hechas a
mano (personajes de palitos)** a pantalla completa, sincronizadas con el guion.

## Guion del video (transcript, provisto por el usuario)
> Si quieres crear contenido pero te da paja mostrar tu cara, esto te va a interesar.
> La mayoría no publica porque no quiere exponerse, no porque no tenga ideas.
> Por eso creamos un avatar que habla por vos. Se ve real, suena real y sos vos quien
> decide qué dice. Ya hay cuentas creciendo así, sin mostrar la cara ni una sola vez.
> Comentá avatar acá abajo si querés aprender cómo armar el tuyo.

## Video base
- Original subido por el usuario: `.mov`, HEVC, **1080x1908**, 30fps, **22.37s**, audio AAC estéreo.
- Transcodificado a H.264 en `video-edit/assets/base.mp4` (los assets están gitignoreados;
  hay que re-transcodificar en cada sesión nueva a partir del `.mov` re-subido).

## Estilo de las imágenes
Marcador negro sobre papel crema, **personajes de palitos**, minimalista/infantil,
mayormente monocromo con UN acento suave (verde-azulado apagado), mucho espacio en
blanco, dinámico, NADA corporativo, **vertical 9:16 a pantalla completa**.

## 6 beats guion → imagen (ver prompts en `generate_images.py`)
| id | Momento | Dibujo |
|----|---------|--------|
| 0_hook_cara | "te da paja mostrar tu cara" | palito se filma pero se tapa la cara |
| 1_ideas_miedo | "no publica... no porque no tenga ideas" | palito lleno de ideas, frenado ante "PUBLICAR" |
| 2_avatar_habla | "un avatar que habla por vos" | palito → flecha → avatar gemelo en el celu hablando |
| 3_real_vos_decidis | "se ve real, suena real, vos decidís" | avatar realista en pantalla + ondas + manito eligiendo |
| 4_crece_sin_cara | "cuentas creciendo... sin mostrar la cara" | flecha/gráfico subiendo + cabeza sin cara + seguidores |
| 5_cta_comenta | "comentá avatar acá abajo" | caja de comentario con "avatar" + flecha grande abajo |

## Extras pedidos antes (mantener en la composición final)
- Overlay "editado por Claude Code" arriba-izquierda, fade-in a los 2s, visible en la intro.
- Fade a negro suave de 0.5s al final.
- Captions: **los hace el usuario** por su cuenta (NO generarlos acá).
- Música: Suno bloqueado; queda para después salvo que el usuario suba un track.

## Estado del pipeline
- [x] Entorno: ffmpeg + ffprobe (apt) + hyperframes CLI 0.8.17 + Chrome headless para render.
- [x] Prompts diseñados → `video-edit/generate_images.py` (paralelo, stdlib, kie.ai Nano Banana, 9:16).
- [ ] Generar las 6 imágenes con la key de kie (requiere red hacia api.kie.ai + file.aiquickdraw.com).
- [ ] Construir composición HyperFrames (video base + 6 imágenes full-screen en los tiempos de cada frase + overlay + fade).
- [ ] Timing de cada imagen: alinear el guion con el audio offline (aeneas: `pip install aeneas`, necesita `espeak`) → timestamps por frase.
- [ ] Preview en browser + render final MP4.

## Red del entorno (por qué se necesita)
El sandbox por defecto (**Trusted**) bloquea api.kie.ai (y OpenAI/Suno/HuggingFace).
Para generar las imágenes hay que poner el entorno en **Custom** con estos dominios
(o **Full**), y arrancar una sesión nueva:
```
api.kie.ai
*.kie.ai
file.aiquickdraw.com
*.aiquickdraw.com
```
(dejar tildado "incluir también la lista default de package managers" para que sigan
funcionando pypi/npm).

## Cómo generar las imágenes (en la sesión nueva con red abierta)
```
cd video-edit
export KIE_API_KEY="<key de kie del usuario>"   # el usuario la pega en el chat; NO commitearla
python3 generate_images.py                        # crea video-edit/avatar_images/*.png
```
Luego seguir con la construcción de la composición.
