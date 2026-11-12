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
FATOR = float(os.environ.get("ROSTO_FATOR", 1.85))   # altura testa→queixo / largura do rosto (selfie de perto)
PONTE = float(os.environ.get("ROSTO_PONTE", 0.03))   # buraco de olho/sobrancelha que a faixa do rosto atravessa (fração da largura)

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
        pele = person & (lab[..., 0] > 42) & (lab[..., 1] > 6) & (lab[..., 2] > 5)
        faixa = 0.24      # faixa da cabeça (enquadramento normal: o rosto inteiro cabe em 24% da tela)
        while True:
            band = np.zeros_like(person); fim = min(H, top + int(H * faixa)); band[top:fim] = True
            skin = (pele & band).astype(np.uint8)
            skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            k, lbl, st, _ = cv2.connectedComponentsWithStats(skin)
            if k <= 1:
                break
            j = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
            x, y, w, h, area = st[j]
            # rosto grande (selfie de perto): a pele encosta no fim da faixa → a faixa cresce até achar o queixo
            if y + h >= fim - 2 and faixa < 0.6 and fim < H:
                faixa += 0.06
                continue
            break
        if k > 1 and area > W * H * 0.003:
            queixo = y + h
            if faixa > 0.24:
                # faixa cresceu (selfie de perto): o queixo sai da proporção do rosto, não do fim da pele (pescoço e mão)
                # largura do rosto entre a testa e os olhos (15–35% da pele), medida só no trecho contínuo de pele que
                # passa pelo centro da testa — mão, braço ou pincel encostados ao lado não contam (antes, com a mão
                # perto do olho, o rosto parecia largo e o queixo ia 18% da tela pra baixo). Altura testa→queixo ≈
                # FATOR × essa largura (calibrado em selfie, IMG_4802)
                comp = (lbl[y:y + h] == j)
                # olhos e sobrancelhas não são pele: fecha esses buracos pra faixa do rosto não parecer estreita
                pontes = cv2.morphologyEx(comp.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((1, max(3, int(W * PONTE))), np.uint8)) > 0
                topo_cols = np.nonzero(comp[:max(2, h // 10)].any(0))[0]
                cx = int(np.median(topo_cols)) if len(topo_cols) else w // 2 + x
                cx = cx - x if len(topo_cols) == 0 else cx
                runs = []
                for r in range(int(h * 0.15), max(int(h * 0.15) + 1, int(h * 0.35))):
                    lin = pontes[r]
                    c = cx if lin[cx] else (np.nonzero(lin)[0][np.argmin(np.abs(np.nonzero(lin)[0] - cx))] if lin.any() else None)
                    if c is None:
                        continue
                    a_ = c
                    while a_ > 0 and lin[a_ - 1]: a_ -= 1
                    b_ = c
                    while b_ < len(lin) - 1 and lin[b_ + 1]: b_ += 1
                    runs.append(b_ - a_ + 1)
                larg = comp.sum(1)
                lf_antiga = float(np.median(larg[int(h * 0.15):max(int(h * 0.15) + 1, int(h * 0.35))]))
                # a menor das duas: sem mão perto são iguais (nada muda); com mão encostada, a mão não conta
                lf = min(lf_antiga, float(np.median(runs))) if runs else lf_antiga
                queixo = y + min(h, int(FATOR * lf))
            # o topo do rosto começa no topo da cabeça (testa coberta pelo cabelo/franja também conta)
            box = [x / W, top / H, (x + w) / W, queixo / H]
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
