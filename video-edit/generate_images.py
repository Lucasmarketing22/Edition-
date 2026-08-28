#!/usr/bin/env python3
"""
Genera imagenes con Nano Banana (kie.ai) EN PARALELO y las descarga.

Estilo: dibujadas a mano, personajes de palitos, colores neutros, 9:16 vertical,
super simples y visuales, pensadas para incrustarse a pantalla completa en el video.

USO
----
1) Necesitas Python 3 (ya viene en Mac/Linux; en Windows instalar desde python.org).
2) Pone tu API key de kie.ai en una variable de entorno y corre el script:

   Mac / Linux:
       export KIE_API_KEY="tu_key_de_kie"
       python3 generate_images.py

   Windows (PowerShell):
       $env:KIE_API_KEY="tu_key_de_kie"
       python3 generate_images.py

3) Las imagenes se guardan en la carpeta ./avatar_images/  (0.png ... 5.png)
   Cuando terminen, subilas al chat (o al repo) y las incrusto en el video.

No usa librerias externas: solo la libreria estandar de Python.
"""

import concurrent.futures as futures
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://api.kie.ai"
CREATE_URL = f"{API_BASE}/api/v1/jobs/createTask"
QUERY_URL = f"{API_BASE}/api/v1/jobs/recordInfo"
MODEL = "google/nano-banana"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatar_images")

# Estilo compartido por TODAS las imagenes (consistencia visual).
STYLE = (
    "Hand-drawn doodle illustration, black felt-tip marker sketch on off-white paper, "
    "simple stick-figure characters with round heads, minimalist childlike drawing that "
    "anyone could understand at a glance, mostly monochrome with ONE soft muted accent "
    "color (dusty teal), lots of clean negative space, friendly and dynamic, casual "
    "imperfect lines, NOT corporate, no gradients, no photorealism. "
    "Vertical 9:16 composition that fills the entire frame, subject centered."
)

# Regla dura anti-texto: el modelo tiende a escribir palabras en ingles, no queremos eso.
NO_TEXT = (
    " IMPORTANT: this is a PURELY VISUAL illustration. Do NOT write any text, words, "
    "letters, numbers, captions, labels or titles anywhere in the image. Buttons and "
    "screens must be blank. Communicate the idea only through the drawing."
)

# 6 beats del guion -> 6 imagenes. Describimos SOLO la escena a dibujar (sin meta-texto).
# keep_text: si es True, se permite el texto minimo definido en el propio prompt.
SCENES = [
    {
        "id": "0_hook_cara",
        "prompt": "A single stick figure holding up a smartphone to film themselves but covering "
                  "their own face with the other hand, looking shy and reluctant, a small teal "
                  "'record' dot glowing above the phone.",
    },
    {
        "id": "1_ideas_miedo",
        "prompt": "A single stick figure standing nervously with a worried face and one sweat drop, "
                  "its head overflowing with many lightbulbs and idea doodles floating all around; "
                  "the figure stands frozen in front of a big blank rounded push-button (the button "
                  "surface is completely empty, no writing).",
    },
    {
        "id": "2_avatar_habla",
        "prompt": "On the left a stick-figure person; a big curved arrow points from them to a "
                  "smartphone on the right; inside the phone screen there is a friendly identical "
                  "stick-figure avatar twin with little curved speech/sound lines coming from its mouth.",
    },
    {
        "id": "3_real_vos_decidis",
        "prompt": "A smartphone held upright with a friendly stick-figure avatar face smiling on the "
                  "screen and curved sound waves radiating on both sides; a small pointing hand/finger "
                  "tapping a little blank toggle next to it, a tiny teal check mark.",
    },
    {
        "id": "4_crece_sin_cara",
        "prompt": "A big bold upward arrow next to a rising bar chart with an ascending trend line, "
                  "and below them a faceless avatar head (a blank oval with NO facial features) with a "
                  "small teal heart on its chest and a rising meter bar going up.",
    },
    {
        "id": "5_cta_comenta",
        "keep_text": True,
        "prompt": "A hand-drawn rounded speech/comment bubble with ONLY the single handwritten "
                  "lowercase word \"avatar\" inside it (dusty teal outline), and directly below the "
                  "bubble a big bold hand-drawn arrow pointing straight DOWN, plus a simple pointing "
                  "finger. The ONLY text anywhere in the whole image is that one word 'avatar' inside "
                  "the bubble — no other letters, words, numbers or captions anywhere.",
    },
]


# User-Agent de navegador: los hosts detras de Cloudflare rechazan el UA de urllib.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _post_json(url, payload, api_key, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url, api_key, timeout=60):
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_task(scene, api_key):
    prompt = f"{scene['prompt']}\n\nSTYLE: {STYLE}"
    if not scene.get("keep_text"):
        prompt += NO_TEXT
    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "output_format": "png",
            "aspect_ratio": "9:16",
            "nsfw_checker": False,
        },
    }
    for attempt in range(4):
        try:
            res = _post_json(CREATE_URL, payload, api_key)
            if res.get("code") == 200:
                return res["data"]["taskId"]
            # 429 rate limit -> backoff and retry
            if res.get("code") == 429:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"createTask fallo: {res.get('code')} {res.get('msg')}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} en createTask: {body}")
    raise RuntimeError("createTask: agotados los reintentos")


def poll_task(task_id, api_key, timeout_s=600):
    deadline = time.time() + timeout_s
    delay = 3.0
    while time.time() < deadline:
        res = _get_json(f"{QUERY_URL}?taskId={task_id}", api_key)
        data = res.get("data") or {}
        state = data.get("state")
        if state == "success":
            result = json.loads(data["resultJson"])
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError("success pero sin resultUrls")
            return urls[0]
        if state == "fail":
            raise RuntimeError(f"fallo: {data.get('failCode')} {data.get('failMsg')}")
        time.sleep(delay)
        delay = min(delay * 1.4, 15.0)  # backoff exponencial suave
    raise RuntimeError("timeout esperando el resultado")


def download(url, dest):
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "image/*,*/*")
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main():
    api_key = os.environ.get("KIE_API_KEY", "").strip()
    if not api_key:
        print("ERROR: falta la variable KIE_API_KEY. Ver instrucciones arriba.", file=sys.stderr)
        sys.exit(1)

    # Argumentos opcionales = ids (o prefijos numericos) a regenerar. Sin args: todas.
    wanted = [a.strip() for a in sys.argv[1:] if a.strip()]
    scenes = SCENES
    if wanted:
        scenes = [s for s in SCENES if s["id"] in wanted or s["id"].split("_")[0] in wanted]
    if not scenes:
        print(f"Nada que generar para: {wanted}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando {len(scenes)} imagenes con Nano Banana...\n", flush=True)

    # 1) Crear todas las tareas EN PARALELO (POST). El createTask soporta la rafaga.
    created = {}
    with futures.ThreadPoolExecutor(max_workers=len(scenes)) as pool:
        futs = {pool.submit(create_task, s, api_key): s["id"] for s in scenes}
        for fut in futures.as_completed(futs):
            name = futs[fut]
            try:
                created[name] = fut.result()
                print(f"[{name}] task creada: {created[name]}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{name}] ERROR creando: {e}", file=sys.stderr, flush=True)

    # 2) Poll + descarga SECUENCIAL (con pausas) para no gatillar el 403 de Cloudflare.
    ok, fail = [], []
    for s in scenes:
        name = s["id"]
        tid = created.get(name)
        if not tid:
            fail.append(name)
            continue
        try:
            url = poll_task(tid, api_key)
            dest = os.path.join(OUT_DIR, f"{name}.png")
            download(url, dest)
            print(f"[{name}] OK -> {dest} ({os.path.getsize(dest)//1024}KB)", flush=True)
            ok.append(name)
        except Exception as e:  # noqa: BLE001
            fail.append(name)
            print(f"[{name}] ERROR: {e}", file=sys.stderr, flush=True)
        time.sleep(1.5)

    print("\n==== RESUMEN ====")
    print(f"OK   ({len(ok)}): {', '.join(ok) or '-'}")
    print(f"FALL ({len(fail)}): {', '.join(fail) or '-'}")
    print(f"\nImagenes en: {OUT_DIR}")
    if fail:
        sys.exit(2)


if __name__ == "__main__":
    main()
