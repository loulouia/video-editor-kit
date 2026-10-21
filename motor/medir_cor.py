"""Diz se o bruto foi gravado com imagem "lavada" (perfil log/flat: preto acinzentado, pouco contraste).

Uso: python motor/medir_cor.py <bruto.mp4>
Imprime JSON: {"lavado": bool, "preto": .., "faixa": .., "saturacao": ..} (média de 3 quadros).

Usado no modo "direto ao resultado" pra escolher a cor sem perguntar: lavado → padroes/amanda/cor/lavado.cube;
normal → cor da marca. Calibração (2026-10-21, poucos vídeos — revisar com mais exemplos):
  Adel Bark original (Sony, lavado): preto 75, faixa 124, saturação 23
  TASTE WASHING 5 (Amanda, normal):   preto 26, faixa 178, saturação 33
"""
import json, subprocess, sys

import cv2
import numpy as np

PRETO_MIN = 45     # 2º percentil da luminância (0–255): acima disso o preto está cinza
FAIXA_MAX = 150    # 98º − 2º percentil: abaixo disso falta contraste

src = sys.argv[1]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                           capture_output=True, text=True).stdout or 0)
medidas = []
for frac in (0.2, 0.5, 0.8):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * frac:.2f}", "-i", src, "-frames:v", "1",
                          "-vf", "scale=360:-2", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    if not raw:
        continue
    h = len(raw) // (360 * 3)
    im = np.frombuffer(raw, np.uint8)[: 360 * h * 3].reshape(h, 360, 3)
    y = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float)
    medidas.append((np.percentile(y, 2), np.percentile(y, 98) - np.percentile(y, 2),
                    cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 1].mean()))
preto, faixa, sat = np.array(medidas).mean(0)
print(json.dumps({"lavado": bool(preto >= PRETO_MIN and faixa < FAIXA_MAX),
                  "preto": round(preto), "faixa": round(faixa), "saturacao": round(sat)}))
