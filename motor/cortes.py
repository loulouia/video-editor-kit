"""Aplica os cortes aprovados (cortes.json), a aceleração e o grading de cor e gera o A-roll.

Uso: python motor/cortes.py projetos/<video> <bruto_local.mp4>
     (copiar o bruto pro scratchpad antes: a Área de Trabalho sincroniza com o iCloud e trava leituras)
Lê de projeto.json: "aceleracao" (PLAYBOOK §2, escolhida no plano), "grading" ("marca" | caminho | null),
"fim" (opcional, segundo do bruto onde o vídeo termina; padrão = duração do bruto).
Saída: composicao/assets/aroll.mp4  +  timeline.json (trechos mantidos e palavras no tempo final)
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
bruto = sys.argv[2]
SPEED = P.p["aceleracao"]
LUT = P.lut()
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", bruto],
                           capture_output=True, text=True).stdout)
FIM = P.p.get("fim", dur)

words = json.load(open(P.path("transcricao/bruto.words.json")))
cuts = sorted((c["de"], c["ate"]) for c in json.load(open(P.path("cortes.json"))))

keep, t = [], 0.0
for a, b in cuts:
    if a > t:
        keep.append((round(t, 3), round(a, 3)))
    t = max(t, b)
keep.append((round(t, 3), round(FIM, 3)))

def to_final(x):
    """Tempo do bruto → tempo final (depois dos cortes e da aceleração)."""
    acc = 0.0
    for a, b in keep:
        if x < a:
            return acc / SPEED
        if x <= b:
            return (acc + x - a) / SPEED
        acc += b - a
    return acc / SPEED

final_words = [dict(w, fs=round(to_final(w["s"]), 3), fe=round(to_final(w["e"]), 3))
               for w in words if w["s"] < FIM and not any(a <= w["s"] < b for a, b in cuts)]
total = sum(b - a for a, b in keep) / SPEED
json.dump({"speed": SPEED, "keep": keep, "duration": round(total, 3), "words": final_words},
          open(P.path("timeline.json"), "w"), ensure_ascii=False, indent=1)

# ffmpeg: recorta cada trecho, micro-fade de áudio (evita estalo), concatena, acelera mantendo o tom e aplica a cor
parts, labels = [], []
for k, (a, b) in enumerate(keep):
    d = b - a
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];"
                 f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{k}];")
    labels.append(f"[v{k}][a{k}]")
lut = f",lut3d='{os.path.abspath(LUT)}'" if LUT else ""
fc = "".join(parts) + "".join(labels) + f"concat=n={len(keep)}:v=1:a=1[vc][ac];" \
     f"[vc]setpts=PTS/{SPEED},fps=30{lut}[v];[ac]atempo={SPEED}[a]"
os.makedirs(P.assets, exist_ok=True)
out = os.path.join(P.assets, "aroll.mp4")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", bruto, "-filter_complex", fc,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)

print(f"trechos mantidos: {len(keep)} | cortes: {len(cuts)} | aceleração {SPEED}× | cor: {os.path.basename(LUT) if LUT else 'original'} | duração final: {total:.2f}s")
for a, b in cuts:
    print(f"  corte {a:6.2f}–{b:6.2f} ({b-a:.2f}s)")
