"""Detector de fala: separa a fala de pausa, RESPIRO e ruído pelo TOM (vibração das cordas vocais), não pelo volume.

Por volume não dá: com o celular perto da boca o respiro chega a -36 dB, tão alto quanto parte da fala (IMG_4802).
A voz tem tom (som periódico, 70–400 Hz); respiro e ruído são chiado (sem tom). Então:
1. "com tom" = periodicidade (autocorrelação normalizada) acima de `tom_min` e volume acima do silêncio + `volume_min_db`;
2. fala = trechos com tom + uma folguinha antes (`antes_s`) e depois (`depois_s`) pras consoantes sem tom
   (o "s" de "delas", o "f", o "ch"), que ficam colados na vogal;
3. o resto (silêncio, respiro, ruído) é "sem fala".
Usado por motor/cortar_pausas.py (corta pausas e respiros) e motor/sincronizar.py (palavra entra quando a fala começa).

fala_ativa(arquivo, cfg) → (t, ativo, volume_db, piso_db), por janela de 10 ms.
"""
import subprocess
import numpy as np

PASSO = 0.01          # 10 ms
JANELA = 640          # 40 ms a 16 kHz
PADRAO = {"tom_min": 0.5, "volume_min_db": 12, "antes_s": 0.08, "depois_s": 0.12}


def audio(arquivo):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arquivo, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768


def medir(arquivo):
    """Por janela de 10 ms: volume (dB), periodicidade (0–1) e o silêncio da sala (percentil 10 do volume)."""
    a = audio(arquivo)
    J = int(16000 * PASSO)
    n = max(0, (len(a) - JANELA) // J)
    q = np.lib.stride_tricks.sliding_window_view(a, JANELA)[::J][:n]
    db = 20 * np.log10(np.sqrt((q ** 2).mean(1)) + 1e-9)
    piso = float(np.percentile(db, 10))
    w = np.hanning(JANELA)
    x = (q - q.mean(1, keepdims=True)) * w
    X = np.fft.rfft(x, 2 * JANELA)
    ac = np.fft.irfft(np.abs(X) ** 2)[:, :JANELA]
    wac = np.fft.irfft(np.abs(np.fft.rfft(w, 2 * JANELA)) ** 2)[:JANELA]
    ac = ac / np.maximum(ac[:, :1], 1e-12) / np.maximum(wac / wac[0], 1e-3)     # corrige o efeito da janela
    lo, hi = 16000 // 400, 16000 // 70                                        # tom entre 70 e 400 Hz
    per = ac[:, lo:hi].max(1)
    per[db < piso + 6] = 0
    t = np.arange(n) * PASSO + JANELA / 2 / 16000
    return t, db, per, piso


def fala_ativa(arquivo, cfg=None):
    c = dict(PADRAO, **(cfg or {}))
    t, db, per, piso = medir(arquivo)
    tom = (per > c["tom_min"]) & (db > piso + c["volume_min_db"])
    # tom isolado < 30 ms é ruído
    k = 0
    while k < len(tom):
        if tom[k]:
            j = k
            while j < len(tom) and tom[j]:
                j += 1
            if j - k < 3:
                tom[k:j] = False
            k = j
        else:
            k += 1
    ativo = tom.copy()
    a, d = int(round(c["antes_s"] / PASSO)), int(round(c["depois_s"] / PASSO))
    for k in np.nonzero(tom)[0]:
        ativo[max(0, k - a):k + d + 1] = True
    return t, ativo, db, piso


def trechos_sem_voz(t, ativo, minimo_s):
    """[(início, fim)] dos trechos sem fala com pelo menos `minimo_s`."""
    out, i = [], 0
    while i < len(ativo):
        if not ativo[i]:
            j = i
            while j < len(ativo) and not ativo[j]:
                j += 1
            if (j - i) * PASSO >= minimo_s:
                out.append((float(t[i]), float(t[min(j, len(t) - 1)])))
            i = j
        else:
            i += 1
    return out
