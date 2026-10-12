"""Refina os cortes: os tempos globais do Whisper derivam, então cada candidato é retranscrito
numa janela curta (tempos locais são precisos) e o corte vai do fim da palavra anterior ao início da próxima.

Candidatos: pausas entre palavras (transcrição global) + silêncios reais (silencedetect).
Depois, SEMPRE validar com motor/energia.py (as bordas e o interior de cada corte precisam estar no ruído da sala).
Uso: python motor/refinar_cortes.py projetos/<video> <bruto_local.mp4>  → grava cortes.json
projeto.json pode ter "cortes_config": {"manter": [[de, ate, "motivo"], ...], "respiro": {"palavra,": segundos}}
"""
import json, os, re, subprocess, sys, tempfile
import mlx_whisper

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

PJ = Projeto(sys.argv[1])
HERE = PJ.dir
bruto = sys.argv[2]
MODEL = "mlx-community/whisper-large-v3-turbo"
MIN_CORTE = 0.12
MARGEM = 0.05
CC = PJ.p.get("cortes_config", {})
MANTER = [tuple(m) for m in CC.get("manter", [])]   # trechos que nunca são cortados (pausas intencionais)
RESPIRO = CC.get("respiro", {})                        # palavra antes do corte → respiro mantido (s)

words = json.load(open(os.path.join(HERE, "transcricao/bruto.words.json")))
cands = [(a["e"] + b["s"]) / 2 for a, b in zip(words, words[1:]) if b["s"] - a["e"] > 0.2]
sil = subprocess.run(["ffmpeg", "-hide_banner", "-i", bruto, "-af", "silencedetect=n=-30dB:d=0.1", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", sil)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", sil)]
cands += [(a + b) / 2 for a, b in zip(st, en) if b - a >= 0.14]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", bruto],
                           capture_output=True, text=True).stdout)
cands = sorted(c for c in cands if 0.5 < c < dur - 0.4)
merged = []
for c in cands:
    if not merged or c - merged[-1] > 0.6:
        merged.append(c)

cuts = []
tmp = tempfile.mkdtemp()
for c in merged:
    if any(a <= c <= b for a, b, _ in MANTER):
        continue
    w0 = max(0, c - 1.5)
    wav = os.path.join(tmp, "w.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{w0}", "-t", "3", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, language="pt", word_timestamps=True)
    lw = [(w["word"].strip(), w0 + w["start"], w0 + w["end"]) for s in r["segments"] for w in s["words"]]
    # par de palavras vizinhas cujo intervalo contém (ou fica mais perto de) c
    best = None
    for (pw, ps, pe), (nw, ns, ne) in zip(lw, lw[1:]):
        gap = ns - pe
        dist = 0 if pe <= c <= ns else min(abs(c - pe), abs(c - ns))
        if gap > 0 and (best is None or (dist, -gap) < (best[0], -best[1])):
            best = (dist, gap, pw, pe, nw, ns)
    if not best or best[0] > 0.4:
        continue
    _, gap, pw, pe, nw, ns = best
    a, b = pe + MARGEM + RESPIRO.get(pw, 0), ns - MARGEM
    if b - a >= MIN_CORTE:
        cuts.append({"de": round(a, 3), "ate": round(b, 3), "entre": f"{pw} | {nw}"})

json.dump(cuts, open(os.path.join(HERE, "cortes.json"), "w"), ensure_ascii=False, indent=1)
for c in cuts:
    print(f"corte {c['de']:6.2f}–{c['ate']:6.2f} ({c['ate']-c['de']:.2f}s)  {c['entre']}")
