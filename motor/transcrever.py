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
gl = open(P.marca(P.M["glossario"]), encoding="utf-8").read().split("## Erros conhecidos")[0] if P.M.get("glossario") else ""
for line in gl.splitlines():
    m = re.match(r"\|\s*([^|]+?)\s*\|", line)
    if m and not set(m.group(1)) <= set("-: ") and m.group(1).lower() not in ("termo", "termos"):
        terms += [t.strip() for t in m.group(1).split(",")]
prompt = f"Vídeo de {P.M['nome']}." + (" Termos: " + ", ".join(terms) + "." if terms else "")

r = mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
                           language="pt", word_timestamps=True, initial_prompt=prompt)
fim_audio = max((seg["end"] for seg in r["segments"]), default=0)

def vale(w, ultimo):
    """Descarta só lixo: token sem letra/número, ou número "alucinado" com duração zero no último instante do áudio.
    Números de um dígito de verdade ("1,", "6") ficam (antes eram descartados e a contagem "1, 2, 3..." sumia)."""
    t = w["word"].strip()
    if not re.search(r"[A-Za-zÀ-ÿ0-9]", t):
        return False
    if ultimo and re.fullmatch(r"[0-9][,.;:!?]*", t) and w["end"] - w["start"] < 0.02 and w["end"] >= fim_audio - 0.1:
        return False
    return True

words, alertas = [], []
for seg in r["segments"]:
    sw = seg.get("words", [])
    ok = [w for k, w in enumerate(sw) if vale(w, k == len(sw) - 1)]
    words += [{"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)} for w in ok]
    # conferência: a frase do trecho tem palavras que não vieram na lista palavra por palavra? (o Whisper às vezes
    # pula palavras no modo palavra por palavra, ex. uma contagem rápida) → avisa com o trecho
    norm = lambda x: re.sub(r"[^\wÀ-ÿ]", "", x.lower())
    frase = [norm(t) for t in seg["text"].split() if norm(t)]
    lista = [norm(w["word"]) for w in ok if norm(w["word"])]
    if len(frase) > len(lista):
        faltam = list(frase)
        for t in lista:
            if t in faltam: faltam.remove(t)
        alertas.append(f"{seg['start']:.2f}–{seg['end']:.2f} s: faltam {len(frase) - len(lista)} palavra(s) na lista "
                       f"({' '.join(faltam[:12])}) — frase: \"{seg['text'].strip()}\"")
os.makedirs(P.path("transcricao"), exist_ok=True)
alerta_arq = P.path(f"transcricao/{nome}.alertas.txt")
if alertas:
    open(alerta_arq, "w", encoding="utf-8").write("\n".join(alertas) + "\n")
    for a in alertas:
        print("⚠️  palavras puladas na transcrição:", a)
    print(f"   → retranscrever esses trechos isolados e inserir as palavras com tempo em transcricao/{nome}.words.json")
elif os.path.exists(alerta_arq):
    os.remove(alerta_arq)
json.dump(words, open(P.path(f"transcricao/{nome}.words.json"), "w"), ensure_ascii=False)
with open(P.path(f"transcricao/{nome}.txt"), "w") as f:
    for seg in r["segments"]:
        f.write(f"[{seg['start']:6.2f}-{seg['end']:6.2f}] {seg['text'].strip()}\n")
print(f"{len(words)} palavras → transcricao/{nome}.words.json")
