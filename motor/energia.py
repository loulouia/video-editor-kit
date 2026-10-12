"""Valida cada corte de cortes.json pela energia do áudio do bruto (CLAUDE.md, lições técnicas).

As bordas de um corte de pausa precisam estar no nível do ruído da sala; se houver voz dentro, o corte come
uma palavra. Para início falso (corte que remove fala de propósito), as bordas precisam cair em vales de energia.

Uso: python motor/energia.py projetos/<video> <bruto_local.mp4> [--perfil de ate]
     --perfil 10.2 11.6  → imprime o perfil de energia (20 ms) do trecho, pra achar os vales à mão
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
