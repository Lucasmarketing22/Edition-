#!/usr/bin/env python3
"""
Genera imagenes con Nano Banana (kie.ai) EN PARALELO desde un scenes.json y las descarga.

scenes.json:
{
  "style": "bloque de estilo compartido (el MISMO personaje en todas)",
  "no_text_rule": "regla anti-texto (ej: no text, words, letters, numbers)",
  "aspect_ratio": "9:16",
  "scenes": [
    {"id": "0_hook",  "prompt": "descripcion de la escena", "keep_text": false},
    {"id": "5_cta",   "prompt": "...con la palabra avatar", "keep_text": true}
  ]
}

Uso:
  KIE_API_KEY=... python3 generate_images.py scenes.json --out avatar_images/
  KIE_API_KEY=... python3 generate_images.py scenes.json --out avatar_images/ --only 2 5

Solo libreria estandar. La descarga usa User-Agent de navegador (Cloudflare bloquea urllib).
"""
import argparse, concurrent.futures as futures, json, os, sys, time, urllib.error, urllib.request

CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
QUERY_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
MODEL = "google/nano-banana"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def post(url, payload, key):
    r = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    r.add_header("Authorization", f"Bearer {key}"); r.add_header("Content-Type", "application/json")
    r.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(r, timeout=60).read())


def get(url, key):
    r = urllib.request.Request(url); r.add_header("Authorization", f"Bearer {key}"); r.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def download(url, dest):
    r = urllib.request.Request(url); r.add_header("User-Agent", UA); r.add_header("Accept", "image/*,*/*")
    with urllib.request.urlopen(r, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def create_task(scene, cfg, key):
    prompt = f"{scene['prompt']}\n\nSTYLE: {cfg.get('style','')}"
    if not scene.get("keep_text"):
        prompt += " " + cfg.get("no_text_rule", "IMPORTANT: no text, words, letters or numbers anywhere.")
    payload = {"model": MODEL, "input": {"prompt": prompt, "output_format": "png",
               "aspect_ratio": cfg.get("aspect_ratio", "9:16"), "nsfw_checker": False}}
    for attempt in range(4):
        try:
            res = post(CREATE_URL, payload, key)
            if res.get("code") == 200:
                return res["data"]["taskId"]
            if res.get("code") == 429:
                time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f"createTask {res.get('code')} {res.get('msg')}")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8','ignore')}")
    raise RuntimeError("createTask: reintentos agotados")


def poll(task_id, key, timeout_s=600):
    deadline = time.time() + timeout_s; delay = 3.0
    while time.time() < deadline:
        d = get(f"{QUERY_URL}?taskId={task_id}", key).get("data") or {}
        st = d.get("state")
        if st == "success":
            urls = json.loads(d["resultJson"]).get("resultUrls") or []
            if not urls:
                raise RuntimeError("success sin resultUrls")
            return urls[0]
        if st == "fail":
            raise RuntimeError(f"fail: {d.get('failCode')} {d.get('failMsg')}")
        time.sleep(delay); delay = min(delay * 1.4, 15.0)
    raise RuntimeError("timeout")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes_json")
    ap.add_argument("--out", default="avatar_images")
    ap.add_argument("--only", nargs="*", default=[], help="ids o prefijos numericos a (re)generar")
    args = ap.parse_args()

    key = os.environ.get("KIE_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: falta KIE_API_KEY")
    cfg = json.load(open(args.scenes_json))
    scenes = cfg["scenes"]
    if args.only:
        scenes = [s for s in scenes if s["id"] in args.only or s["id"].split("_")[0] in args.only]
    if not scenes:
        sys.exit("Nada que generar")

    os.makedirs(args.out, exist_ok=True)
    print(f"Generando {len(scenes)} imagenes...\n", flush=True)

    created = {}
    with futures.ThreadPoolExecutor(max_workers=len(scenes)) as pool:
        futs = {pool.submit(create_task, s, cfg, key): s["id"] for s in scenes}
        for fut in futures.as_completed(futs):
            name = futs[fut]
            try:
                created[name] = fut.result(); print(f"[{name}] task {created[name]}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{name}] ERROR crear: {e}", file=sys.stderr, flush=True)

    ok, fail = [], []
    for s in scenes:
        name = s["id"]; tid = created.get(name)
        if not tid:
            fail.append(name); continue
        try:
            url = poll(tid, key); dest = os.path.join(args.out, f"{name}.png"); download(url, dest)
            print(f"[{name}] OK -> {dest} ({os.path.getsize(dest)//1024}KB)", flush=True); ok.append(name)
        except Exception as e:  # noqa: BLE001
            fail.append(name); print(f"[{name}] ERROR: {e}", file=sys.stderr, flush=True)
        time.sleep(1.5)

    print(f"\nOK {len(ok)}: {', '.join(ok) or '-'}\nFALL {len(fail)}: {', '.join(fail) or '-'}")
    if fail:
        sys.exit(2)


if __name__ == "__main__":
    main()
