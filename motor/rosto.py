"""Mapeia onde está o rosto ao longo do vídeo (PLAYBOOK §0 — nada cobre o rosto).

Usa o recorte (alfa) da pessoa + cor de pele: dentro da máscara, na faixa da cabeça, a pele é a parte clara
e rosada (o cabelo é escuro). A caixa do rosto é o maior bloco de pele perto do topo da pessoa.

Uso: python rosto.py <video.mp4> <recorte.webm> <saida.json> [--fps 4] [--debug pasta]
     python rosto.py <video.mp4> --rapido <saida.json>   → sem recorte pronto: recorta só 2 quadros/s (~15 s),
                                                           pro storyboard (motor/storyboard.py)
Saída: {"fps": 4, "rostos": [[t, x0, y0, x1, y1], ...]} em fração da tela (0–1), no enquadramento ORIGINAL
(sem zoom e sem o deslocamento do fundo mesclado; quem posiciona aplica as transformações).
"""
import argparse, json, os, subprocess
import cv2
import numpy as np

import sys, tempfile
if "--rapido" in sys.argv:                 # modo storyboard: recorte só de 2 quadros por segundo
    video, saida = sys.argv[1], sys.argv[sys.argv.index("--rapido") + 1]
    tmp = tempfile.mkdtemp(); clip, matte = os.path.join(tmp, "q.mp4"), os.path.join(tmp, "q.webm")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-an", "-vf", "fps=2,scale=540:960",
                    "-c:v", "libx264", "-crf", "18", clip], check=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "remove-background", clip, "-o", matte], capture_output=True, check=True)
    sys.argv = [sys.argv[0], clip, matte, saida, "--fps", "2"]
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("recorte"); ap.add_argument("saida")
ap.add_argument("--fps", type=float, default=4); ap.add_argument("--debug")
A = ap.parse_args()
W, H = 270, 480

def frames(args, pix, ch):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error"] + args + ["-vf", f"fps={A.fps},scale={W}:{H}" + (",format=rgba,alphaextract" if pix == "gray" else ""),
                          "-f", "rawvideo", "-pix_fmt", pix, "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, ch) if ch > 1 else np.frombuffer(raw, np.uint8).reshape(-1, H, W)

rgb = frames(["-i", A.video], "rgb24", 3)
alpha = frames(["-c:v", "libvpx-vp9", "-i", A.recorte], "gray", 1)
n = min(len(rgb), len(alpha))
out, last = [], None
for i in range(n):
    person = alpha[i] > 128
    rows = np.nonzero(person.sum(1) > W * 0.04)[0]
    box = None
    if len(rows):
        top = rows[0]
        lab = cv2.cvtColor(rgb[i].astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        band = np.zeros_like(person); band[top: min(H, top + int(H * 0.24))] = True
        skin = (person & band & (lab[..., 0] > 42) & (lab[..., 1] > 6) & (lab[..., 2] > 5)).astype(np.uint8)
        skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        k, lbl, st, _ = cv2.connectedComponentsWithStats(skin)
        if k > 1:
            j = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
            x, y, w, h, area = st[j]
            if area > W * H * 0.003:
                # o topo do rosto começa no topo da cabeça (testa coberta pelo cabelo/franja também conta)
                box = [x / W, top / H, (x + w) / W, (y + h) / H]
    box = box or last
    if box:
        out.append([round(i / A.fps, 2)] + [round(v, 4) for v in box]); last = box
    if A.debug and box and i % 8 == 0:
        os.makedirs(A.debug, exist_ok=True)
        im = cv2.cvtColor(rgb[i], cv2.COLOR_RGB2BGR).copy()
        cv2.rectangle(im, (int(box[0] * W), int(box[1] * H)), (int(box[2] * W), int(box[3] * H)), (0, 255, 255), 2)
        cv2.imwrite(os.path.join(A.debug, f"rosto_{i/A.fps:05.1f}.jpg"), im)
json.dump({"fps": A.fps, "rostos": out}, open(A.saida, "w"))
print(f"{len(out)} amostras; queixo (y1) mín {min(r[4] for r in out):.2f} máx {max(r[4] for r in out):.2f}")
