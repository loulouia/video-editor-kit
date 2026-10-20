"""Baixa do Drive o que um vídeo precisa pra ser editado (ou reaberto): o bruto e as inserções.

Uso: python motor/preparar.py projetos/<slug>
  → cache/bruto.<ext>                      (cópia local temporária; apagada na entrega)
  → composicao/assets/img/<inserções>      (imagens e b-roll de insercoes/<nome-do-bruto>/)
Imprime o caminho do bruto local, pra usar nos outros passos do motor.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive

pj = os.path.abspath(sys.argv[1])
p = json.load(open(os.path.join(pj, "projeto.json"), encoding="utf-8"))
ext = os.path.splitext(p["bruto"])[1].lower() or ".mp4"
bruto = os.path.join(pj, "cache", "bruto" + ext)
if not os.path.exists(bruto):
    drive.baixar(p["bruto_drive"], bruto)
ins = drive.baixar_pasta(p["insercoes_drive"], os.path.join(pj, "composicao", "assets", "img"))
print(json.dumps({"bruto_local": bruto, "insercoes": ins}, ensure_ascii=False))
