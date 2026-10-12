"""Transcreve com tempos por palavra (mlx-whisper, rápido em Mac com chip M), usando o glossário da MARCA como contexto.

Uso: python motor/transcrever.py projetos/<video> <audio_ou_video> <nome_saida>
     ex.: ... bruto.mp4 bruto   → transcricao/bruto.words.json + transcricao/bruto.txt
          ... composicao/assets/aroll.mp4 aroll
Os tempos globais derivam até ~1 s: nunca cortar só com base neles (ver motor/energia.py).
"""
import json, os, re, sys
import mlx_whisper

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
audio, nome = sys.argv[2], sys.argv[3]

# Termos certos: primeira coluna das tabelas do glossário da marca (antes da seção de erros conhecidos)
terms = []
gl = open(P.marca(P.M["glossario"]), encoding="utf-8").read().split("## Erros conhecidos")[0]
for line in gl.splitlines():
    m = re.match(r"\|\s*([^|]+?)\s*\|", line)
    if m and not set(m.group(1)) <= set("-: ") and m.group(1).lower() not in ("termo", "termos"):
        terms += [t.strip() for t in m.group(1).split(",")]
prompt = f"Vídeo de {P.M['nome']}. Termos: " + ", ".join(terms) + "."

r = mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
                           language="pt", word_timestamps=True, initial_prompt=prompt)
words = [{"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)}
         for seg in r["segments"] for w in seg["words"]]
# o Whisper às vezes "alucina" números/vírgulas no último instante do áudio: descarta tokens sem letras
words = [w for w in words if re.search(r"[A-Za-zÀ-ÿ0-9]{2,}|^[A-Za-zÀ-ÿ]$", w["w"]) and w["e"] > w["s"] - 0.01]
os.makedirs(P.path("transcricao"), exist_ok=True)
json.dump(words, open(P.path(f"transcricao/{nome}.words.json"), "w"), ensure_ascii=False)
with open(P.path(f"transcricao/{nome}.txt"), "w") as f:
    for seg in r["segments"]:
        f.write(f"[{seg['start']:6.2f}-{seg['end']:6.2f}] {seg['text'].strip()}\n")
print(f"{len(words)} palavras → transcricao/{nome}.words.json")
