#!/usr/bin/env python3
"""
Genera imagenes con Nano Banana (kie.ai) EN PARALELO y las descarga.

Estilo: STICKMAN moderno estilo "faceless YouTube" — monigote blanco con cara
expresiva y buzo rojo, contornos limpios, dinamico, colorido, 9:16 vertical.
Pensadas como B-roll: aparecen unos segundos sobre el avatar y se van.

USO
----
    export KIE_API_KEY="tu_key_de_kie"
    python3 generate_images.py            # genera las 6
    python3 generate_images.py 2 5        # regenera solo esas (por prefijo)

Las imagenes se guardan en ./avatar_images/. Solo usa la libreria estandar.
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

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Estilo compartido: el MISMO personaje stickman en todas (consistencia).
STYLE = (
    "Modern clean 'faceless YouTube' stickman cartoon illustration. The SAME recurring "
    "character in every image: a simple WHITE stick-figure with thin black stick arms and "
    "legs, a round white head with BIG expressive cartoon eyes and an expressive mouth, "
    "wearing a bright RED hoodie. Bold clean black outlines, smooth flat vector shading, "
    "vibrant and energetic, small motion lines for dynamism, clean light near-white "
    "background. Vertical 9:16, subject centered."
)

NO_TEXT = (
    " IMPORTANT: purely visual illustration. Do NOT write any text, words, letters, numbers, "
    "captions or labels anywhere. Buttons and screens are blank. Communicate only by drawing."
)

# 6 beats del guion -> 6 imagenes (mismo personaje stickman de buzo rojo).
SCENES = [
    {
        "id": "0_hook_cara",
        "prompt": "The red-hoodie stickman holds up a smartphone to film itself but shyly covers "
                  "its own face with its other hand, looking bashful; a small glowing red record "
                  "dot above the phone; playful motion lines.",
    },
    {
        "id": "1_ideas_miedo",
        "prompt": "The red-hoodie stickman stands nervously with a worried face and one sweat drop, "
                  "its head surrounded by many glowing lightbulbs and swirling idea doodles; it is "
                  "frozen in front of a big blank rounded push-button (the button is completely empty).",
    },
    {
        "id": "2_avatar_habla",
        "prompt": "On the left the red-hoodie stickman; a big bold curved arrow points to the right "
                  "toward a smartphone; inside the phone screen there is a friendly identical stickman "
                  "avatar twin with little curved speech/sound lines coming from its mouth.",
    },
    {
        "id": "3_real_vos_decidis",
        "prompt": "A large smartphone held upright with a friendly stickman avatar face smiling on the "
                  "screen and curved sound waves radiating on both sides; the red-hoodie stickman's hand "
                  "points and taps a small blank toggle beside it; a small green check mark, thumbs up.",
    },
    {
        "id": "4_crece_sin_cara",
        "prompt": "A big bold upward arrow next to a rising bar chart with an ascending trend line; "
                  "below, a faceless avatar head (a blank oval with NO facial features) with a small "
                  "heart and a rising meter bar; the red-hoodie stickman stands beside it giving a thumbs up.",
    },
    {
        "id": "5_cta_comenta",
        "keep_text": True,
        "prompt": "The red-hoodie stickman points upward at a rounded speech/comment bubble that "
                  "contains ONLY the single handwritten lowercase word \"avatar\"; directly below the "
                  "bubble a big bold arrow points straight DOWN. The ONLY text anywhere is that one word "
                  "'avatar' inside the bubble — no other letters, words or numbers.",
    },
]


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
            if res.get("code") == 429:
                time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f"createTask fallo: {res.get('code')} {res.get('msg')}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1)); continue
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
            urls = (json.loads(data["resultJson"]).get("resultUrls") or [])
            if not urls:
                raise RuntimeError("success pero sin resultUrls")
            return urls[0]
        if state == "fail":
            raise RuntimeError(f"fallo: {data.get('failCode')} {data.get('failMsg')}")
        time.sleep(delay)
        delay = min(delay * 1.4, 15.0)
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
        print("ERROR: falta la variable KIE_API_KEY.", file=sys.stderr)
        sys.exit(1)

    wanted = [a.strip() for a in sys.argv[1:] if a.strip()]
    scenes = SCENES
    if wanted:
        scenes = [s for s in SCENES if s["id"] in wanted or s["id"].split("_")[0] in wanted]
    if not scenes:
        print(f"Nada que generar para: {wanted}", file=sys.stderr); sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando {len(scenes)} imagenes (stickman) con Nano Banana...\n", flush=True)

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

    ok, fail = [], []
    for s in scenes:
        name = s["id"]; tid = created.get(name)
        if not tid:
            fail.append(name); continue
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
