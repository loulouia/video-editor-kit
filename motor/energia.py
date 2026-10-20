"""Valida cada corte de cortes.json pela energia do áudio do bruto (CLAUDE.md, lições técnicas).

As bordas de um corte de pausa precisam estar no nível do ruído da sala; se houver voz dentro, o corte come
uma palavra. Para início falso (corte que remove fala de propósito), as bordas precisam cair em vales de energia.

Uso: python motor/energia.py projetos/<video> <bruto_local.mp4> [--perfil de ate | --sugerir [fim] [--gravar]]
     --perfil 10.2 11.6  → imprime o perfil de energia (20 ms) do trecho, pra achar os vales à mão
     --sugerir 40.4      → propõe cortes nas pausas reais (energia abaixo do piso da sala por > 0,25 s);
                           com --gravar, substitui cortes.json (início falso continua à mão). Melhor em sala silenciosa
"""
import json, os, subprocess, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1]); bruto = sys.argv[2]
raw = os.path.join(tempfile.mkdtemp(), "a.raw")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", raw], check=True)
a = np.fromfile(raw, np.int16).astype(float)

def db(t0, t1):
    s = a[int(t0 * 16000):int(t1 * 16000)]
    return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9) - 90

if "--perfil" in sys.argv:
    i = sys.argv.index("--perfil"); lo, hi = float(sys.argv[i + 1]), float(sys.argv[i + 2])
    for t in np.arange(lo, hi, 0.02):
        d = db(t, t + 0.02); print(f"{t:.2f} {d:6.1f} " + "#" * int(max(0, d + 50)))
    sys.exit(0)

floor = np.percentile([db(i / 50, (i + 1) / 50) for i in range(int(len(a) / 320))], 10)
print(f"piso de ruído: {floor:.1f} dB (borda ok se < {floor + 12:.1f} dB)")

if "--sugerir" in sys.argv:
    # pausas reais: trechos de 20 ms abaixo de piso+10 dB por mais de 0,25 s → corte deixando 0,06 s de cada lado
    i = sys.argv.index("--sugerir"); prox = sys.argv[i + 1] if len(sys.argv) > i + 1 else ""
    fim = float(prox) if prox and not prox.startswith("--") else len(a) / 16000
    quiet = [db(t, t + 0.02) < floor + 10 for t in np.arange(0, fim, 0.02)]
    novos, start = [], None
    for k, q in enumerate(quiet + [False]):
        if q and start is None: start = k
        if not q and start is not None:
            s0, s1 = start * 0.02, k * 0.02
            if s1 - s0 >= 0.25 and s0 > 0.3 and s1 < fim - 0.1:
                novos.append({"de": round(s0 + 0.06, 3), "ate": round(s1 - 0.06, 3), "entre": f"pausa {s1-s0:.2f}s (energia)"})
            start = None
    for c in novos:
        print(f"sugestão {c['de']:6.2f}–{c['ate']:6.2f} ({c['ate']-c['de']:.2f}s)")
    if "--gravar" in sys.argv:
        json.dump(novos, open(P.path("cortes.json"), "w"), ensure_ascii=False, indent=1); print(f"{len(novos)} cortes gravados em cortes.json")
    sys.exit(0)
ruins = 0
for c in json.load(open(P.path("cortes.json"))):
    x, y = c["de"], c["ate"]
    e1, e2 = db(x - 0.03, x), db(y, y + 0.03)
    falso = "início falso" in c.get("entre", "")
    inside = max(db(t, t + 0.02) for t in np.arange(x, max(x + 0.021, y - 0.02), 0.01))
    ok = max(e1, e2) < floor + 12 and (falso or inside < floor + 12)
    ruins += not ok
    print(f"{'OK ' if ok else '⚠️ '} {x:6.2f}–{y:6.2f}  bordas {e1:6.1f}/{e2:6.1f}  dentro máx {inside:6.1f}  | {c.get('entre', '')}")
print("todos os cortes validados" if not ruins else f"{ruins} corte(s) a revisar (use --perfil pra achar os vales)")
