"""Divide a fala em legendas respeitando o padrão: no máximo `linhas_max` linhas de `caracteres_por_linha`
(PLAYBOOK §4 de cada padrão). Prefere quebrar em pontuação; nunca deixa uma palavra sozinha no fim.

Uso: python motor/legendas.py projetos/<video> [--de <indice> --ate <indice>] [--gravar]
     Lê transcricao/aroll.words.json e imprime as legendas; com --gravar, escreve em edicao.json → "legendas"
     (formato [texto, índice_da_primeira_palavra, índice_da_última]). Revisar a grafia pelo glossário da marca
     antes de gravar: o texto vem do Whisper.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
L = P.S["legenda"]
MAXC = L.get("caracteres_por_linha", 30) * L.get("linhas_max", 2)
ALVO = int(MAXC * 0.88)          # mira abaixo do máximo (na referência, a maioria fica entre 25 e 55 caracteres)
# palavras de ligação: uma legenda nunca termina nelas (vão pra legenda seguinte)
LIGACAO = {"pra", "para", "de", "do", "da", "dos", "das", "que", "e", "o", "a", "os", "as", "um", "uma",
           "no", "na", "nos", "nas", "com", "em", "por", "se", "eu", "você", "the", "a", "to", "of", "and", "in"}
W = json.load(open(P.path("transcricao/aroll.words.json"), encoding="utf-8"))
a = int(sys.argv[sys.argv.index("--de") + 1]) if "--de" in sys.argv else 0
b = int(sys.argv[sys.argv.index("--ate") + 1]) if "--ate" in sys.argv else len(W) - 1

def fmt(ws):
    t = " ".join(w["w"] for w in ws).strip()
    return t.upper() if L.get("maiusculas", True) else t[:1].lower() + t[1:] if t[:2] != t[:2].upper() else t

caps, cur = [], []
for i in range(a, b + 1):
    w = W[i]
    if cur and len(fmt(cur + [w])) > ALVO:          # não cabe: fecha a legenda atual
        cut = len(cur)
        # recua palavras de ligação do fim e a palavra solta depois de uma vírgula
        while cut > 2 and cur[cut - 1]["w"].lower().strip(",.") in LIGACAO:
            cut -= 1
        if cut == len(cur) and cut > 2 and cur[-2]["w"][-1] in ",;:" and cur[-1]["w"][-1] not in ".?!,":
            cut -= 1
        caps.append(cur[:cut]); cur = cur[cut:]
    cur.append(w)
    end = w["w"][-1]
    if end in ".?!" and len(fmt(cur)) >= 12:          # fim de frase fecha a legenda
        caps.append(cur); cur = []
    elif end in ",;:" and len(fmt(cur)) >= ALVO * 0.6: # vírgula depois de ~60% do limite também fecha
        caps.append(cur); cur = []
if cur:
    caps.append(cur)
# sobra curta (menos de 12 caracteres) junta na legenda anterior, se couber no máximo
k = 1
while k < len(caps):
    if len(fmt(caps[k])) < 12 and len(fmt(caps[k - 1] + caps[k])) <= MAXC:
        caps[k - 1] = caps[k - 1] + caps.pop(k)
    else:
        k += 1

idx = {id(w): k for k, w in enumerate(W)}
out = [[fmt(c).rstrip(","), idx[id(c[0])], idx[id(c[-1])]] for c in caps]
for t, i, j in out:
    print(f"{W[i]['s']:6.2f}  [{len(t):2d}] {t}")
if "--gravar" in sys.argv:
    e = P.edicao(); e["legendas"] = out
    json.dump(e, open(P.path("edicao.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(out)} legendas gravadas (máx. {MAXC} caracteres, {L.get('linhas_max', 2)} linhas)")
