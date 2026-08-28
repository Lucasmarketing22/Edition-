#!/usr/bin/env python3
"""
Genera musica instrumental con Suno (kie.ai), la recorta a la duracion del video con fades
y la deja lista para mezclar de fondo (~15-20%).

Uso:
  KIE_API_KEY=... python3 generate_music.py --mood "calm soft piano underscore, relaxing" \
      --seconds 22.4 --out assets/music/bgm.mp3

Notas:
- El endpoint de Suno EXIGE callBackUrl -> se pasa uno dummy y se hace polling.
- Suno devuelve tracks largos (~2-3 min); se recorta a --seconds con fade in/out.
- Requiere ffmpeg en PATH para el recorte.
"""
import argparse, json, os, subprocess, sys, time, urllib.request

GEN_URL = "https://api.kie.ai/api/v1/generate"
REC_URL = "https://api.kie.ai/api/v1/generate/record-info"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def post(url, payload, key):
    r = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    r.add_header("Authorization", f"Bearer {key}"); r.add_header("Content-Type", "application/json")
    r.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(r, timeout=60).read())


def get(url, key):
    r = urllib.request.Request(url); r.add_header("Authorization", f"Bearer {key}"); r.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mood", required=True, help="descripcion del instrumental")
    ap.add_argument("--seconds", type=float, default=22.0)
    ap.add_argument("--model", default="V4")
    ap.add_argument("--out", default="assets/music/bgm.mp3")
    args = ap.parse_args()
    key = os.environ.get("KIE_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: falta KIE_API_KEY")

    payload = {"prompt": f"{args.mood}. Instrumental, no vocals, unobtrusive background underscore.",
               "customMode": False, "instrumental": True, "model": args.model,
               "callBackUrl": "https://example.com/callback"}
    res = post(GEN_URL, payload, key)
    tid = res["data"]["taskId"]; print("taskId:", tid, flush=True)

    audio = None
    for i in range(90):
        d = get(f"{REC_URL}?taskId={tid}", key).get("data", {})
        st = d.get("status"); print(i, st, flush=True)
        for t in (d.get("response") or {}).get("sunoData") or []:
            audio = t.get("audioUrl") or t.get("streamAudioUrl") or audio
        if st == "SUCCESS" and audio:
            break
        if st in ("CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED", "SENSITIVE_WORD_ERROR", "CALLBACK_EXCEPTION"):
            sys.exit(f"FAIL: {json.dumps(d)[:400]}")
        time.sleep(6)
    if not audio:
        sys.exit("no se obtuvo audio")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    raw = args.out + ".raw.mp3"
    req = urllib.request.Request(audio); req.add_header("User-Agent", UA)
    open(raw, "wb").write(urllib.request.urlopen(req, timeout=180).read())

    fade_out = max(0.0, args.seconds - 1.5)
    subprocess.run(["ffmpeg", "-y", "-ss", "0.3", "-t", f"{args.seconds}", "-i", raw,
                    "-af", f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out}:d=1.5",
                    "-c:a", "libmp3lame", "-q:a", "3", args.out], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(raw)
    print("OK ->", args.out, os.path.getsize(args.out) // 1024, "KB")


if __name__ == "__main__":
    main()
