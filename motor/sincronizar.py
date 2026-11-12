"""Acerta o começo de cada palavra (transcricao/aroll.words.json) pela voz real do A-roll.

O Whisper marca o começo das palavras ADIANTADO (medido no IMG_4802: 56 de 286 palavras entravam antes da voz,
até 0,45 s). Na legenda palavra por palavra isso aparece: a palavra surge antes de ser falada.
Usa o detector de fala (motor/voz.py: decide pelo tom; respiro e ruído não contam como fala):
1. Palavra cujo começo cai perto de um início de voz (silêncio/respiro → fala, entre -0,2 e +0,45 s) → começa
   exatamente nesse início.
2. Senão (fala corrida): atrasa pela mediana do erro medido nas palavras do caso 1 (entre 0 e 0,2 s).
3. Regra final: a palavra NUNCA começa num trecho sem voz — se cair em silêncio/respiro, espera a voz voltar.
O atraso estimado não passa do fim da palavra; nunca volta antes da anterior. Idempotente: guarda o tempo do Whisper em "s0".

Uso: python motor/sincronizar.py projetos/<video>     (depois de transcrever o A-roll, antes de legendas.py)
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto
from voz import fala_ativa, PASSO

P = Projeto(sys.argv[1])
arq = P.path("transcricao/aroll.words.json")
W = json.load(open(arq, encoding="utf-8"))
for w in W:
    w.setdefault("s0", w["s"])

t, ativo, e, piso = fala_ativa(os.path.join(P.assets, "aroll.mp4"), P.S.get("cortes", {}))
n = len(ativo)
idx = lambda x: min(n - 1, max(0, int(round(x / PASSO))))
inicios = [k for k in range(1, n) if ativo[k] and not ativo[k - 1]]       # silêncio/respiro → voz
inicios_t = np.array([t[k] for k in inicios]) if inicios else np.array([])


def inicio_perto(s0):
    if not len(inicios_t):
        return None
    perto = inicios_t[(inicios_t >= s0 - 0.2) & (inicios_t <= s0 + 0.45)]
    return float(perto[np.argmin(np.abs(perto - (s0 + 0.1)))]) if len(perto) else None


def proxima_voz(x):
    k = idx(x)
    while k < n and not ativo[k]:
        k += 1
    return float(t[min(k, n - 1)])


achados = {k: inicio_perto(w["s0"]) for k, w in enumerate(W)}
dif = [v - W[k]["s0"] for k, v in achados.items() if v is not None]
atraso = float(min(0.2, max(0.0, np.median(dif)))) if dif else 0.0

ant, movidas = 0.0, 0
for k, w in enumerate(W):
    s = achados[k] if achados[k] is not None else w["s0"] + atraso
    s = min(s, max(w["s0"], w["e"] - 0.05))     # o atraso estimado não passa do fim da palavra
    s = max(s, ant)
    if not ativo[idx(s)]:                       # regra mais forte: nunca em silêncio/respiro, espera a voz
        s = proxima_voz(s)
    movidas += abs(s - w["s0"]) > 0.02
    w["s"] = round(s, 3)
    ant = w["s"]
json.dump(W, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{sum(v is not None for v in achados.values())} palavras alinhadas no início da voz; as da fala corrida "
      f"atrasadas {atraso*1000:.0f} ms; {movidas} palavras mudaram (erro do Whisper: mediana "
      f"{np.median(dif)*1000 if dif else 0:+.0f} ms)")
