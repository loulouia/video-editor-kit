"""Junta num único vídeo as camadas que precisam da pessoa recortada na frente (uma cópia só, sem "fantasma"):
fundo mesclado (PLAYBOOK 4.5) e texto atrás da pessoa (PLAYBOOK 3.2).

Fundo mesclado: o vídeo desce até o topo da cabeça ficar em `cabeca_alvo` da altura (medido no recorte),
a imagem ocupa o topo (>= 50%) com degradê, e a pessoa recortada vai por cima. Corte seco na entrada/saída.

Valores (proporção, cabeça alvo, texto atrás) vêm do PADRÃO; o que vai em cada trecho vem de edicao.json.
Uso:     python motor/compor_camadas.py projetos/<video>
Entrada: composicao/assets/aroll.mp4, cache/subject.webm, edicao.json
Saída:   composicao/assets/aroll_comp.mp4  +  cache/camadas.json (deslocamentos medidos)
"""
import json, os, shutil, subprocess, sys
import cv2
import numpy as np
from matplotlib.ft2font import FT2Font

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
AS = P.assets
AROLL, SUB = os.path.join(AS, "aroll.mp4"), P.path("cache/subject.webm")
OUT = os.path.join(AS, "aroll_comp.mp4")
TMP = P.path("cache/camadas"); os.makedirs(TMP, exist_ok=True)
E = P.edicao()
C = P.fundo_mesclado()
TA = P.S["texto_atras"]
ZOOM = P.zoom()
W, H, FPS, D = 1080, 1920, 30, E["duracao"]
FONT = P.padrao(P.S["fonte"]["arquivo"])

if not E["topo_mesclado"] and not E["texto_atras"]:      # nada pra embutir: o vídeo único é o próprio A-roll
    shutil.copy2(AROLL, OUT)
    json.dump({"deslocamentos_px": [], "janelas": []}, open(P.path("cache/camadas.json"), "w"), indent=1)
    print("sem camadas: aroll_comp = aroll"); sys.exit(0)


def ffpipe(path, w, h):
    """Abre um ffmpeg que recebe quadros RGBA crus e grava um .mov com alfa (PNG)."""
    return subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                             "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "png", path], stdin=subprocess.PIPE)


# ---------- 1. topo da cabeça em cada trecho de fundo mesclado (pelo alfa do recorte) ----------
def head_top(a, b):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-c:v", "libvpx-vp9", "-ss", f"{a}", "-t", f"{b-a}", "-i", SUB,
                          "-vf", "fps=4,scale=270:480,format=rgba,alphaextract", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270)
    tops = []
    for f in fr:
        rows = np.nonzero((f > 128).sum(axis=1) > 270 * 0.06)[0]   # ignora fios soltos e mãos finas
        if len(rows):
            tops.append(rows[0] / 480)
    return float(np.median(tops))

shifts = []
for t in E["topo_mesclado"]:
    top = head_top(t["de"], t["ate"])
    s = int(np.clip((C["cabeca_alvo"] - top) * H, 0, C["deslocamento_max"] * H)) // 2 * 2
    shifts.append(s)
    print(f"fundo mesclado {t['de']:.2f}–{t['ate']:.2f}: cabeça em {top*100:.1f}% → desce {s}px ({s/H*100:.1f}%)")

# ---------- 2. camada da imagem do topo (cover, Ken Burns leve, degradê no pé) ----------
LH = int(C["altura_imagem"] * H)
mask = np.ones(LH, np.float32)
g0 = int(C["degrade_de"] * H)
mask[g0:] = np.linspace(1, 0, LH - g0)
topo_movs = []
ZL = C["zoom_lento"]
for k, t in enumerate(E["topo_mesclado"]):
    n_img = len(t["imagens"]); step = (t["ate"] - t["de"]) / n_img
    covers = []
    for img in t["imagens"]:
        im = cv2.cvtColor(cv2.imread(os.path.join(AS, img), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        sc = max(W * ZL / im.shape[1], LH * ZL / im.shape[0])
        covers.append(cv2.resize(im, (round(im.shape[1] * sc), round(im.shape[0] * sc)), interpolation=cv2.INTER_AREA))
    path = os.path.join(TMP, f"topo{k}.mov"); p = ffpipe(path, W, LH)
    n = round((t["ate"] - t["de"]) * FPS)
    for i in range(n):
        m = min(int(i / FPS / step), n_img - 1)
        prog = (i / FPS - m * step) / step
        cv_ = covers[m]; z = ZL / (1 + (ZL - 1) * prog)              # zoom lento de 1,00 até zoom_lento
        cw = round(W * z); ch = round(LH * z)
        x0 = (cv_.shape[1] - cw) // 2; y0 = int((cv_.shape[0] - ch) * C["posicao_vertical_imagem"])
        crop = cv2.resize(cv_[y0:y0 + ch, x0:x0 + cw], (W, LH), interpolation=cv2.INTER_AREA)
        rgba = np.dstack([crop, (mask[:, None] * 255).astype(np.uint8).repeat(W, 1)])
        p.stdin.write(rgba.tobytes())
    p.stdin.close(); p.wait()
    topo_movs.append((t["de"], t["ate"], path))

# ---------- 3. texto atrás da pessoa ----------
def render_text(txt, size, track=-0.045):
    f = FT2Font(FONT); f.set_size(size, 72)
    glyphs, x = [], 0.0
    for ch in txt:
        f.set_text(ch); f.draw_glyphs_to_bitmap()
        bmp = np.asarray(f.get_image()); ox, oy = f.get_bitmap_offset()
        adv = f.get_width_height()[0] / 64
        glyphs.append((x, bmp, f.get_descent() / 64))
        x += adv + track * size
    asc = size * 0.95; h = int(size * 1.3); canvas = np.zeros((h, int(x + size * 0.2)), np.float32)
    for gx, bmp, desc in glyphs:
        top = int(asc - (bmp.shape[0] - desc)); xx = int(gx)
        canvas[top:top + bmp.shape[0], xx:xx + bmp.shape[1]] = np.maximum(canvas[top:top + bmp.shape[0], xx:xx + bmp.shape[1]], bmp / 255.0)
    ys, xs = np.nonzero(canvas > 0.02)
    return canvas[ys.min():ys.max() + 1, xs.min():xs.max() + 1]      # só a tinta das letras

atras_movs = []
for k, a in enumerate(E["texto_atras"]):
    ink = render_text(a["texto"], TA["tamanho_px"], TA["espacamento"])
    # largura alvo: ~80% da tela já descontando o zoom (jump cut) que estiver ativo no trecho
    z = max([ZOOM["escala"] for z0, z1 in ZOOM["trechos"] if z0 <= a["de"] < z1] or [1.0])
    target = TA["largura"] * W / z
    if ink.shape[1] > target:
        f = target / ink.shape[1]
        ink = cv2.resize(ink, (round(ink.shape[1] * f), round(ink.shape[0] * f)), interpolation=cv2.INTER_AREA)
    BH, BY = 520, int(TA["topo"] * H)                       # faixa da camada; topo das letras a ~21% da altura
    path = os.path.join(TMP, f"atras{k}.mov"); p = ffpipe(path, W, BH)
    n = round((a["ate"] - a["de"]) * FPS)
    for i in range(n):
        t = i / FPS; dur = a["ate"] - a["de"]
        pin = min(1, t / 0.3); e = 1 - (1 - pin) ** 3              # entrada: sobe 80px e sai do desfoque
        pout = max(0, (t - (dur - 0.2)) / 0.2)                     # saída: desfoca e some
        alpha = np.zeros((BH, W), np.float32)
        y = int(100 + 80 * (1 - e)); x = (W - ink.shape[1]) // 2
        hh = min(ink.shape[0], BH - y); alpha[y:y + hh, x:x + ink.shape[1]] = ink[:hh]
        blur = 18 * (1 - e) + 12 * pout
        if blur > 0.5:
            alpha = cv2.GaussianBlur(alpha, (0, 0), blur / 2)
        op = e * (1 - pout)
        sh = cv2.GaussianBlur(np.roll(alpha, 10, axis=0), (0, 0), 20) * TA["sombra"]   # sombra suave pra leitura na parede clara
        a_tot = np.clip(alpha + sh * (1 - alpha), 0, 1) * op
        col = np.where(a_tot > 0, alpha * op / np.maximum(a_tot, 1e-6), 0)    # branco onde é letra, preto onde é sombra
        rgb = (np.clip(col, 0, 1)[..., None] * 255).repeat(3, 2).astype(np.uint8)
        p.stdin.write(np.dstack([rgb, (a_tot * 255).astype(np.uint8)]).tobytes())
    p.stdin.close(); p.wait()
    atras_movs.append((a["de"], a["ate"], path, BY))

# ---------- 4. composição final com ffmpeg ----------
yexpr = "+".join(f"{s}*between(t,{t['de']},{t['ate']})" for s, t in zip(shifts, E["topo_mesclado"])) or "0"
win_sub = [(t["de"], t["ate"]) for t in E["topo_mesclado"]] + [(a, b) for a, b, *_ in atras_movs]
args = ["ffmpeg", "-loglevel", "error", "-y", "-i", AROLL, "-c:v", "libvpx-vp9", "-i", SUB]
for a, b, path in topo_movs:
    args += ["-itsoffset", f"{a}", "-i", path]
for a, b, path, _ in atras_movs:
    args += ["-itsoffset", f"{a}", "-i", path]
fc = [f"color=black:s={W}x{H}:r={FPS}:d={D}[bg]",
      f"[bg][0:v]overlay=x=0:y='{yexpr}':eval=frame:shortest=1[b0]"]
cur, idx = "b0", 2
for n, (a, b, _) in enumerate(topo_movs):
    fc.append(f"[{cur}][{idx}:v]overlay=0:0:eof_action=pass:enable='between(t,{a},{b})'[t{n}]"); cur, idx = f"t{n}", idx + 1
for n, (a, b, _, by) in enumerate(atras_movs):
    fc.append(f"[{cur}][{idx}:v]overlay=0:{by}:eof_action=pass:enable='between(t,{a},{b})'[x{n}]"); cur, idx = f"x{n}", idx + 1
en = "+".join(f"between(t,{a},{b})" for a, b in win_sub)
fc.append(f"[{cur}][1:v]overlay=x=0:y='{yexpr}':eval=frame:enable='{en}',format=yuv420p[v]")
args += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium",
         "-crf", "16", "-c:a", "copy", "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
json.dump({"deslocamentos_px": shifts, "janelas": [[t["de"], t["ate"]] for t in E["topo_mesclado"]]},
          open(P.path("cache/camadas.json"), "w"), indent=1)
print("gerado:", OUT)
