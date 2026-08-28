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

# 6 beats del guion -> 6 imagenes. 'text' es lo que se dice; 'scene' es el dibujo.
SCENES = [
    {
        "id": "0_hook_cara",
        "prompt": "A stick figure holding up a smartphone to film themselves but covering "
                  "their own face with one hand, looking shy/reluctant, a small question mark "
                  "and a 'record' dot above. Idea: wanting to make content but not wanting to "
                  "show your face.",
    },
    {
        "id": "1_ideas_miedo",
        "prompt": "A stick figure with many lightbulbs and thought bubbles floating around its "
                  "head (full of ideas), but standing frozen in front of a big 'PUBLISH' button, "
                  "hesitating, a nervous sweat drop. Idea: people have ideas but are afraid to "
                  "expose themselves.",
    },
    {
        "id": "2_avatar_habla",
        "prompt": "A stick-figure person on the left with an arrow pointing to a friendly digital "
                  "avatar 'twin' of the same figure inside a phone screen on the right, the avatar "
                  "has little speech lines coming out of its mouth. Idea: an avatar that speaks for you.",
    },
    {
        "id": "3_real_vos_decidis",
        "prompt": "A realistic-looking avatar face inside a phone screen with sound waves next to it, "
                  "and a small hand/cursor choosing words from a little list, thumbs up. "
                  "Idea: it looks real, it sounds real, and YOU decide what it says.",
    },
    {
        "id": "4_crece_sin_cara",
        "prompt": "A rising growth arrow and a bar chart going up, next to a faceless avatar head "
                  "(blank oval, no face) with a heart and a rising follower counter. "
                  "Idea: accounts are already growing this way without ever showing a face.",
    },
    {
        "id": "5_cta_comenta",
        "prompt": "A big hand-drawn comment box containing the handwritten word \"avatar\", with a "
                  "big arrow and a pointing finger aiming down at it. Idea: comment the word "
                  "'avatar' below to learn how to build your own.",
    },
]


def _post_json(url, payload, api_key, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url, api_key, timeout=60):
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_task(scene, api_key):
    payload = {
        "model": MODEL,
        "input": {
            "prompt": f"{scene['prompt']}\n\nSTYLE: {STYLE}",
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
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def run_one(scene, api_key):
    name = scene["id"]
    task_id = create_task(scene, api_key)
    print(f"[{name}] task creada: {task_id}", flush=True)
    url = poll_task(task_id, api_key)
    dest = os.path.join(OUT_DIR, f"{name}.png")
    download(url, dest)
    print(f"[{name}] OK -> {dest}", flush=True)
    return name, dest


def main():
    api_key = os.environ.get("KIE_API_KEY", "").strip()
    if not api_key:
        print("ERROR: falta la variable KIE_API_KEY. Ver instrucciones arriba.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando {len(SCENES)} imagenes EN PARALELO con Nano Banana...\n", flush=True)

    ok, fail = [], []
    # Todas al mismo tiempo (una por hilo).
    with futures.ThreadPoolExecutor(max_workers=len(SCENES)) as pool:
        futs = {pool.submit(run_one, s, api_key): s["id"] for s in SCENES}
        for fut in futures.as_completed(futs):
            name = futs[fut]
            try:
                fut.result()
                ok.append(name)
            except Exception as e:  # noqa: BLE001
                fail.append((name, str(e)))
                print(f"[{name}] ERROR: {e}", file=sys.stderr, flush=True)

    print("\n==== RESUMEN ====")
    print(f"OK   ({len(ok)}): {', '.join(sorted(ok)) or '-'}")
    print(f"FALL ({len(fail)}): {', '.join(n for n, _ in fail) or '-'}")
    print(f"\nImagenes en: {OUT_DIR}")
    if fail:
        sys.exit(2)


if __name__ == "__main__":
    main()
