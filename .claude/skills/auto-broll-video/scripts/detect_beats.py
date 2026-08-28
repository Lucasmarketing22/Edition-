#!/usr/bin/env python3
"""
Detecta los segmentos de habla de un audio usando ffmpeg silencedetect.
Sirve para ubicar cada imagen B-roll en el momento de su frase, sin transcripcion.

Uso:
  python3 detect_beats.py assets/audio.mp3
  python3 detect_beats.py assets/audio.mp3 --noise -30 --min-silence 0.35

Imprime JSON con:
  duration, silences[], segments[] (tramos de habla entre pausas), midpoints[]
Sugerencia: pone cada insert ~centrado en el midpoint de su frase, ~2s de duracion.
"""
import argparse, json, re, subprocess, sys


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(out.stdout.strip() or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--noise", default="-30", help="umbral dB (default -30)")
    ap.add_argument("--min-silence", default="0.35", help="silencio minimo en s (default 0.35)")
    args = ap.parse_args()

    dur = ffprobe_duration(args.audio)
    proc = subprocess.run(["ffmpeg", "-i", args.audio, "-af",
                           f"silencedetect=noise={args.noise}dB:d={args.min_silence}", "-f", "null", "-"],
                          capture_output=True, text=True)
    log = proc.stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]

    # Construir tramos de habla entre pausas.
    silences = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else dur
        silences.append((s, e))
    segments = []
    cursor = 0.0
    for s, e in silences:
        if s - cursor > 0.25:
            segments.append([round(cursor, 3), round(s, 3)])
        cursor = e
    if dur - cursor > 0.25:
        segments.append([round(cursor, 3), round(dur, 3)])

    mids = [round((a + b) / 2, 3) for a, b in segments]
    print(json.dumps({"duration": round(dur, 3),
                      "silences": [[round(a, 3), round(b, 3)] for a, b in silences],
                      "segments": segments, "midpoints": mids}, indent=2))


if __name__ == "__main__":
    main()
