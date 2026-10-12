"""Gera uma LUT de cor (.cube) que leva o bruto até a coloração/iluminação de uma referência (PLAYBOOK 1.1).

Mede, em espaço Lab, só quadros da pessoa falando nas referências (o usuário passa os tempos) e quadros
espalhados do bruto. A correção é uma transferência de média/desvio por canal (Reinhard), amortecida pra não
distorcer a pele: a média de cor (temperatura/tinta) vai inteira; contraste e saturação vão parcialmente.

Uso:
  python grading.py --bruto bruto.mp4 --ref ref1.mp4:5,6,7,13 --ref ref2.mp4:4.5,19,20 \
                    --saida assets/cor/meus-editados.cube --comparar comparacao.jpg [--intensidade 1.0]
"""
import argparse, os, subprocess
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--bruto", required=True)
ap.add_argument("--ref", action="append", required=True, help="video:t1,t2,... (tempos com a pessoa falando)")
ap.add_argument("--saida", required=True)
ap.add_argument("--comparar")
ap.add_argument("--intensidade", type=float, default=1.0)
A = ap.parse_args()

def frame(path, t, w=270):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1",
                          "-vf", f"scale={w}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    h = len(raw) // (w * 3)
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def lab(rgb):
    return cv2.cvtColor(rgb.astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)

def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)

def person_masks(frames):
    """Máscara da pessoa em cada quadro, usando o recorte local do HyperFrames (mesmo modelo do pipeline)."""
    import tempfile
    tmp = tempfile.mkdtemp()
    h, w = frames[0].shape[:2]
    src, out = os.path.join(tmp, "q.mp4"), os.path.join(tmp, "q.webm")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", "1", "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", src], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(cv2.resize(f, (w, h)).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["npx", "-y", "hyperframes@latest", "remove-background", src, "-o", out], capture_output=True, check=True)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-c:v", "libvpx-vp9", "-i", out, "-vf", "format=rgba,alphaextract",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)[: len(frames)] > 128

def regions(rgb, person):
    """Só o que se repete entre vídeos: pele do rosto + fundo (sala, fora da pessoa).
    A roupa muda de vídeo pra vídeo e não pode entrar na medição."""
    h, w = rgb.shape[:2]
    bg = ~person
    bg[int(h * 0.75):, :] = False                                  # embaixo costuma ter sofá/chão diferentes
    skin = np.zeros((h, w), bool)
    rows = np.nonzero(person.sum(1) > w * 0.04)[0]
    if len(rows):
        top = rows[0]
        band = np.zeros((h, w), bool); band[top + int(h * 0.025): top + int(h * 0.10), :] = True   # testa/rosto
        L = lab(rgb)
        skin = person & band & (L[..., 0] > 40) & (L[..., 1] > 4)   # tira cabelo (escuro) e armação/lentes
    return skin, bg

def stats(frames):
    sk, bg = [], []
    masks = person_masks(frames)
    for f, m in zip(frames, masks):
        L = lab(f); s, b = regions(f, m)
        sk.append(L[s]); bg.append(L[b])
    sk, bg = np.concatenate(sk), np.concatenate(bg)
    bg = bg[(bg[:, 0] > 20) & (bg[:, 0] < 97)]                     # tira objetos muito escuros (TV) e estouro
    if len(sk) < 200:
        raise SystemExit("rosto não detectado em quadros suficientes; escolha outros tempos")
    allpx = np.concatenate([sk, bg])
    # média de cor: metade pele, metade fundo (a pele manda no tom; o fundo, no balanço de branco)
    mean = 0.5 * sk.mean(0) + 0.5 * bg.mean(0)
    return mean, allpx.std(0), sk.mean(0), bg.mean(0)

ref_frames = []
for spec in A.ref:
    path, ts = spec.rsplit(":", 1)
    ref_frames += [frame(path, float(t), 540) for t in ts.split(",")]
dur = duration(A.bruto)
src_frames = [frame(A.bruto, t, 540) for t in np.linspace(0.5, dur - 0.5, 16)]
mt, st, mt_sk, mt_bg = stats(ref_frames)
ms, ss, ms_sk, ms_bg = stats(src_frames)
print("pele   ref", mt_sk.round(1), "| bruto", ms_sk.round(1))
print("fundo  ref", mt_bg.round(1), "| bruto", ms_bg.round(1))

# força da transferência por canal: L (brilho), a (verde↔magenta), b (azul↔amarelo)
MEAN_K = np.array([0.8, 1.0, 1.0]) * A.intensidade        # média: cor inteira, brilho 80%
STD_K = np.array([0.6, 0.5, 0.5]) * A.intensidade         # contraste/saturação: parcial
gain = 1 + STD_K * (st / ss - 1)
shift = MEAN_K * (mt - ms)

def grade_lab(L):
    return (L - ms) * gain + ms + shift

# LUT 33×33×33 (ordem .cube: R varia mais rápido)
N = 33
g = np.linspace(0, 1, N, dtype=np.float32)
b_, g_, r_ = np.meshgrid(g, g, g, indexing="ij")
grid = np.stack([r_, g_, b_], -1).reshape(-1, 1, 3)
out = cv2.cvtColor(grade_lab(cv2.cvtColor(grid, cv2.COLOR_RGB2LAB).reshape(-1, 3)).reshape(-1, 1, 3).astype(np.float32),
                   cv2.COLOR_LAB2RGB).reshape(-1, 3)
out = np.clip(out, 0, 1)
os.makedirs(os.path.dirname(os.path.abspath(A.saida)), exist_ok=True)
with open(A.saida, "w") as f:
    f.write(f'TITLE "grading {os.path.basename(A.saida)}"\nLUT_3D_SIZE {N}\n')
    for r, gg, b in out:
        f.write(f"{r:.6f} {gg:.6f} {b:.6f}\n")

print("referência  L/a/b média", mt.round(1), "desvio", st.round(1))
print("bruto       L/a/b média", ms.round(1), "desvio", ss.round(1))
print("LUT gravada:", A.saida)

if A.comparar:  # bruto | com grading | referência, 3 momentos
    rows = []
    for k, t in enumerate(np.linspace(dur * 0.15, dur * 0.85, 3)):
        raw = frame(A.bruto, t, 360)
        graded = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t}", "-i", A.bruto, "-frames:v", "1",
                                 "-vf", f"lut3d='{A.saida}',scale=360:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                capture_output=True).stdout
        graded = np.frombuffer(graded, np.uint8).reshape(raw.shape)
        ref = cv2.resize(frame(*A.ref[k % len(A.ref)].rsplit(":", 1)[0:1], float(A.ref[k % len(A.ref)].rsplit(":", 1)[1].split(",")[0]), w=360), (raw.shape[1], raw.shape[0]))
        row = np.hstack([raw, graded, ref])
        rows.append(row)
    img = cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR)
    for i, lbl in enumerate(["BRUTO", "COM GRADING", "REFERENCIA"]):
        cv2.putText(img, lbl, (i * 360 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imwrite(A.comparar, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("comparação:", A.comparar)
