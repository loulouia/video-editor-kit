"""Corta pausas E respiros do bruto pelo detector de fala (motor/voz.py: decide pelo TOM, não pelo volume) e grava cortes.json.

Todo trecho sem fala (silêncio, respiro, ruído) com pelo menos `pausa_min_s` vira corte, deixando `margem_antes_s`
depois do fim da fala e `margem_depois_s` antes da fala voltar. A fala já inclui uma folguinha pras consoantes sem tom
(`antes_s`/`depois_s`), então o fim das palavras não é comido.
Também corta o começo (antes da primeira fala) e grava o fim em projeto.json ("fim").
Valores no padrão: padrao.json → "cortes": {"tom_min", "volume_min_db", "antes_s", "depois_s", "pausa_min_s",
"margem_antes_s", "margem_depois_s"}.
Trechos marcados em projeto.json → "cortes_config": {"manter": [[de, ate, "motivo"], ...]} nunca são cortados.

Uso: python motor/cortar_pausas.py projetos/<video> <bruto>
Depois: motor/cortes.py → retranscrever o A-roll e comparar com a transcrição do bruto (nenhuma palavra pode sumir).
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto
from voz import fala_ativa, trechos_sem_voz

P = Projeto(sys.argv[1])
bruto = sys.argv[2]
C = P.S.get("cortes", {})
MIN = C.get("pausa_min_s", 0.2)
MA, MD = C.get("margem_antes_s", 0.0), C.get("margem_depois_s", 0.0)
MANTER = [tuple(m[:2]) for m in P.p.get("cortes_config", {}).get("manter", [])]

t, ativo, e, piso = fala_ativa(bruto, C)
fala = [float(t[k]) for k in range(len(t)) if ativo[k]]
ini_fala, fim_fala = fala[0], fala[-1]

cortes = [{"de": 0.0, "ate": round(max(0.0, ini_fala - MD), 3), "motivo": "início"}] if ini_fala - MD > 0.05 else []
for a, b in trechos_sem_voz(t, ativo, MIN):
    if a <= ini_fala or b >= fim_fala:
        continue
    de, ate = a + MA, b - MD
    if ate - de < 0.05 or any(x < ate and y > de for x, y in MANTER):
        continue
    cortes.append({"de": round(de, 3), "ate": round(ate, 3), "motivo": "pausa/respiro"})
json.dump(cortes, open(P.path("cortes.json"), "w"), ensure_ascii=False, indent=1)
P.p["fim"] = round(fim_fala + 0.3, 3)
json.dump(P.p, open(P.path("projeto.json"), "w"), ensure_ascii=False, indent=1)
tirado = sum(c["ate"] - c["de"] for c in cortes)
print(f"silêncio da sala {piso:.1f} dB | {len(cortes)} cortes, {tirado:.1f} s tirados (pausas e respiros com {MIN:g} s "
      f"ou mais) | fim {P.p['fim']} s")
