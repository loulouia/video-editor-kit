"""Reabre um vídeo já entregue pra ajustar: baixa bruto e inserções e remonta tudo a partir das decisões guardadas.

Uso: python motor/reabrir.py projetos/<slug> [--versao-entregue | --padrao-atual]
  --versao-entregue  (padrão) usa o motor e o padrão guardados na última entrega → abre IGUAL ao que foi entregue
  --padrao-atual     usa o motor e o padrão de hoje (aplica regras novas)
Leva ~5–10 min (o recorte da pessoa é a etapa mais lenta). No fim, abrir o preview.
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
pj = os.path.abspath(sys.argv[1])
p = json.load(open(os.path.join(pj, "projeto.json"), encoding="utf-8"))
env = dict(os.environ, VE_RAIZ=RAIZ)
motor = AQUI
if "--padrao-atual" not in sys.argv and p.get("entregas"):
    ver = os.path.join(pj, p["entregas"][-1]["versao"])
    motor = os.path.join(ver, "motor")
    if os.path.exists(os.path.join(ver, "padrao.json")):
        env["VE_PADRAO_FIXO"] = os.path.join(ver, "padrao.json")
PY = [sys.executable, "-I"]

def rodar(*cmd, **kw):
    print("→", " ".join(os.path.basename(c) if c.endswith(".py") else c for c in cmd[:3]), flush=True)
    subprocess.run(list(cmd), check=True, env=env, **kw)

info = json.loads(subprocess.run(PY + [os.path.join(AQUI, "preparar.py"), pj], check=True, capture_output=True,
                                 text=True, env=env).stdout)
rodar(*PY, os.path.join(motor, "cortes.py"), pj, info["bruto_local"])
rodar("npx", "-y", "hyperframes@latest", "remove-background", os.path.join(pj, "composicao/assets/aroll.mp4"),
      "-o", os.path.join(pj, "cache/subject.webm"), capture_output=True)
rodar(*PY, os.path.join(motor, "rosto.py"), os.path.join(pj, "composicao/assets/aroll.mp4"),
      os.path.join(pj, "cache/subject.webm"), os.path.join(pj, "cache/rosto.json"), capture_output=True)
rodar(*PY, os.path.join(motor, "compor_camadas.py"), pj)
rodar(*PY, os.path.join(motor, "gerar.py"), pj)
print("pronto: abrir o preview em", os.path.join(pj, "composicao"))
