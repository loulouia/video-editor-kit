"""Gera <projeto>/composicao/index.html (HyperFrames) a partir de edicao.json + transcricao/aroll.words.json,
usando os valores do PADRÃO (padroes/<nome>/padrao.json) e da MARCA (marcas/<nome>/marca.json).

Uso: python motor/gerar.py projetos/<video>
"""
import html, json, os, shutil, sys
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
S, M = P.S, P.M
E = P.edicao()
W = json.load(open(P.path("transcricao/aroll.words.json"), encoding="utf-8"))
D = E["duracao"]
ZOOM = P.zoom()
r3 = lambda x: round(x, 3)
esc = html.escape

# ---------- arquivos do padrão e da marca dentro da composição ----------
os.makedirs(os.path.join(P.assets, "fonts"), exist_ok=True)
os.makedirs(os.path.join(P.assets, "img"), exist_ok=True)
FONT_FILE = os.path.basename(S["fonte"]["arquivo"])
shutil.copy2(P.padrao(S["fonte"]["arquivo"]), os.path.join(P.assets, "fonts", FONT_FILE))
for k in ("escuro", "claro"):
    shutil.copy2(P.marca(M["logo"][k]), os.path.join(P.assets, "img", f"logo-{k}.png"))
FW = S["fonte"]["peso"]
FW_RANGE = S["fonte"].get("pesos", FW)        # fonte variável: faixa de pesos ("300 900")
FC = S.get("fonte_cartoes")
if FC:
    for k in ("arquivo", "italico"):
        shutil.copy2(P.padrao(FC[k]), os.path.join(P.assets, "fonts", os.path.basename(FC[k])))

# ---------- janelas ----------
KW, CAP, TIT, CARD, TELA = S["palavras_chave"], S["legenda"], S["titulo"], S["cards"], S["tela"]
kws = []
for k in E["palavras_chave"]:
    idx = [i for _, _, ids in k["partes"] for i in ids]
    kws.append((W[min(idx)]["s"] - 0.05, min(D, W[max(idx)]["e"] + k["segura"]), k))
atras = [(a["de"], a["ate"], a) for a in E["texto_atras"]]
T = E.get("titulo")
blocked = [(a, b) for a, b, _ in kws] + [(a, b) for a, b, _ in atras] + \
          ([(T["de"], T["ate"])] if T and S["titulo"].get("bloqueia_legenda", True) else [])
cards = [(c["de"], c["ate"], c) for c in E["cards"]]

def overlaps(a, b, spans):
    return any(a < y and b > x for x, y in spans)

# ---------- rosto: nada pode cobrir o rosto (PLAYBOOK §0) ----------
_rf = P.path("cache/rosto.json") if os.path.exists(P.path("cache/rosto.json")) else P.path("cache/rosto_rapido.json")
FACE = json.load(open(_rf))["rostos"]     # rosto_rapido.json = modo storyboard (antes do recorte completo)
SHIFT = json.load(open(P.path("cache/camadas.json"))) if os.path.exists(P.path("cache/camadas.json")) else {"janelas": [], "deslocamentos_px": []}
ZS, ZO = ZOOM["escala"], float(ZOOM["origem"].split()[1].rstrip("%")) / 100
SAFE_TOP, SAFE_BOTTOM, GAP = TELA["seguro_topo"], TELA["seguro_base"], TELA["folga_rosto"]

def face_span(a, b):
    """Topo e queixo do rosto (fração da tela) no pior caso dentro de [a, b], já com deslocamento e zoom."""
    tops, chins = [], []
    for t, x0, y0, x1, y1 in FACE:
        if a - 0.15 <= t <= b + 0.15:
            for (w0, w1), s in zip(SHIFT["janelas"], SHIFT["deslocamentos_px"]):
                if w0 <= t <= w1:
                    y0 += s / 1920; y1 += s / 1920
            if any(z0 <= t < z1 for z0, z1 in ZOOM["trechos"]):
                y0, y1 = ZO + (y0 - ZO) * ZS, ZO + (y1 - ZO) * ZS
            tops.append(y0); chins.append(y1)
    return (min(tops), max(chins)) if tops else (0.2, 0.45)

def place(a, b, height, default_top, below_only=False):
    """Topo do elemento: o padrão, empurrado pra baixo do queixo; se não couber, acima do rosto."""
    ftop, chin = face_span(a, b)
    top = max(default_top, chin + GAP)
    if top + height > SAFE_BOTTOM and not below_only and ftop - GAP - height >= SAFE_TOP:
        return round(ftop - GAP - height, 4)
    # sobe pra caber na tela, mas nunca acima do queixo (o rosto não cede; quem não couber encolhe)
    return round(max(chin + GAP, min(top, SAFE_BOTTOM - height)), 4)

# ---------- legendas: começam na 1ª palavra, terminam na próxima legenda / bloqueio ----------
caps = []
for n, (txt, i, j) in enumerate(E["legendas"]):
    s = W[i]["s"]
    e = W[j]["e"] + CAP["fim_extra_s"]
    if n + 1 < len(E["legendas"]):
        e = min(e, W[E["legendas"][n + 1][1]]["s"])
    for x, y in blocked:
        if x <= s < y:      # começa durante uma palavra-chave/título → espera ela sair
            s = y
        elif x > s:
            e = min(e, x)
    if e - s < 0.2:
        continue
    caps.append((r3(s), r3(e), txt, overlaps(s, e, [(a, b) for a, b, _ in cards])))

MAXC = CAP.get("caracteres_por_linha", 30) * CAP.get("linhas_max", 2)
for _, _, txt, _ in caps:
    if len(txt) > MAXC:
        print(f"⚠️  legenda com {len(txt)} caracteres (máx. {MAXC}): {txt!r} — divida com motor/legendas.py")

# Trechos de fundo mesclado: a pessoa está mais baixa na tela → legendas e palavras-chave descem (PLAYBOOK 4.5)
topo_win = [(t["de"], t["ate"]) for t in E["topo_mesclado"]]
caps = [(a, b, txt, up, overlaps(a, b, topo_win)) for a, b, txt, up in caps]

# ---------- HTML ----------
out, tl = [], []
add = out.append

# Vídeo único: fundo mesclado, texto atrás e recorte já embutidos por compor_camadas.py (uma cópia só da pessoa)
video = "aroll_comp.mp4" if os.path.exists(os.path.join(P.assets, "aroll_comp.mp4")) else "aroll.mp4"
add(f'<div id="cam" class="cam"><video id="aroll" src="assets/{video}" playsinline data-has-audio="true" '
    f'data-start="0" data-duration="{D}" data-track-index="0"></video></div>')

# ---------- posições pelo rosto (nada cobre o rosto) ----------
CAP_H, TITLE_H = CAP["altura"], TIT["altura"]

def card_h(c):
    if c["tipo"] == "noticia":
        im = cv2.imread(os.path.join(P.assets, c["arquivo"]))
        return min(CARD["altura_noticia_max"], CARD["largura"] * 1080 * im.shape[0] / im.shape[1] / 1920)
    return CARD["altura_pequeno"] if c["tipo"] == "card-pequeno" else CARD["altura"]

card_pos = []   # (a, b, cabeçalho_top, card_top, card_h)
for a, b, c in cards:
    head = TITLE_H if T and overlaps(a, b, [(T["de"], T["ate"])]) else CAP_H
    ch = card_h(c)
    region = place(a, b, head + GAP + ch, CARD["posicao"])
    ct = region + head + GAP
    if ct + ch > SAFE_BOTTOM:                 # não cabe inteiro: o card encolhe, nunca sobe no rosto
        ch = max(CARD["altura_min"], SAFE_BOTTOM - ct)
    card_pos.append((a, b, region, ct, ch))

def header_top(a, b):
    for x, y, ht, *_ in card_pos:
        if a < y and b > x:
            return ht
    return None

CE = CARD["entrada"]
for n, ((a, b, c), (_, _, _, ct, ch)) in enumerate(zip(cards, card_pos)):
    cid = f"card{n}"
    if c["tipo"] == "noticia":   # encolhe mantendo a proporção do print (nunca corta a manchete)
        im = cv2.imread(os.path.join(P.assets, c["arquivo"]))
        wpx = min(CARD["largura"] * 1080, ch * 1920 * im.shape[1] / im.shape[0])
        size = f"width:{wpx / 1080 * 100:.2f}%"
    else:
        size = f"height:{ch*100:.2f}%"
    add(f'<div id="{cid}" class="clip card-slot" data-start="{r3(a)}" data-duration="{r3(b-a)}" data-track-index="4">'
        f'<div class="card {c["tipo"]}" style="top:{ct*100:.2f}%;{size}"><img src="assets/{c["arquivo"]}" alt=""></div></div>')
    prev_end = cards[n - 1][1] if n else -1
    if abs(prev_end - a) > 0.05:  # entrada só quando não é troca direta de card
        tl.append(f'tl.fromTo("#{cid} .card", {{opacity: 0, scale: {CE["escala_inicial"]}}}, {{opacity: 1, scale: 1, duration: {CE["duracao"]}, ease: "power2.out"}}, {r3(a)});')

COL = TIT.get("colagem")
if T and COL and T.get("colagem"):
    # Gancho com colagem (PLAYBOOK topo-livre §5): 3 imagens no alto, título encostado na base, subtítulo fino
    cw = COL["largura"]; gap = (1 - COL["quantidade"] * cw) / (COL["quantidade"] + 1)
    imgs = "".join(f'<img src="assets/{im}" alt="" style="position:absolute;left:{(gap + i*(cw+gap))*100:.2f}%;top:{COL["topo"]*100:.2f}%;'
                   f'width:{cw*100:.2f}%;height:{COL["altura"]*100:.2f}%;object-fit:cover;">' for i, im in enumerate(T["colagem"]))
    # quebra por caracteres por linha (padrão), sem diminuir a letra
    texto, MAXL, linhas_t = " ".join(T["linhas"]), TIT.get("caracteres_por_linha", 99), []
    for w in texto.split():
        if linhas_t and len(linhas_t[-1] + " " + w) <= MAXL:
            linhas_t[-1] += " " + w
        else:
            linhas_t.append(w)
    if T.get("subtitulo") and len(T["subtitulo"]) > TIT.get("subtitulo_max_caracteres", 999):
        print(f"⚠️  subtítulo com {len(T['subtitulo'])} caracteres (máx. {TIT['subtitulo_max_caracteres']})")
    sh = "" if TIT.get("sombra", "none") == "none" else f'text-shadow:{TIT["sombra"]};'
    # posições finais calculadas no navegador pelo contorno real das letras (fitTitle)
    sub = (f'<div class="t-fit-sub" data-alvo="{TIT["subtitulo_largura"]}" data-folga="{TIT["subtitulo_folga"]}" '
           f'style="position:absolute;left:0;right:0;text-align:center;white-space:nowrap;font-weight:{TIT["subtitulo_peso"]};{sh}">'
           f'{esc(T["subtitulo"])}</div>') if T.get("subtitulo") else ""
    add(f'<div id="titulo" class="clip titulo" data-start="{T["de"]}" data-duration="{r3(T["ate"]-T["de"])}" data-track-index="5">{imgs}'
        + "".join(f'<div class="t-fit" data-linha="{i}" data-alvo="{TIT["largura_alvo"]}" data-topo="{TIT["topo_letras"]}" '
                  f'data-letras="{TIT.get("altura_letras", 0.047)}" data-entre="{TIT.get("entrelinha_letras", 1.28)}" style="position:absolute;left:0;right:0;text-align:center;'
                  f'white-space:nowrap;font-weight:{TIT["peso"]};letter-spacing:{TIT["espacamento"]};{sh}">{esc(l)}</div>' for i, l in enumerate(linhas_t))
        + f'{sub}</div>')
elif T:
    lines = "".join(f'<div class="t-line">{esc(l)}</div>' for l in T["linhas"])
    tt = header_top(T["de"], T["ate"])
    tt = tt if tt is not None else place(T["de"], T["ate"], TITLE_H, TIT["posicao"])
    sub = f'<div class="t-sub">{esc(T["subtitulo"])}</div>' if T.get("subtitulo") else ""
    add(f'<div id="titulo" class="clip titulo" data-start="{T["de"]}" data-duration="{r3(T["ate"]-T["de"])}" data-track-index="5">'
        f'<div class="t-block" style="top:{tt*100:.2f}%">{lines}{sub}</div></div>')

# ---------- caixa do topo (PLAYBOOK topo-livre §2) ----------
CX = S.get("caixa_topo")
CARD_FACES = ""
if FC:
    CARD_FACES = (f'@font-face {{ font-family: "Cartao"; src: url("assets/fonts/{os.path.basename(FC["arquivo"])}"); font-style: normal; }}\n'
                  f'@font-face {{ font-family: "Cartao"; src: url("assets/fonts/{os.path.basename(FC["italico"])}"); font-style: italic; }}')
if CX and E.get("caixa_topo"):
    PAL = dict(S["cartoes"]["paleta_neutra"]); PAL.update(M.get("paleta", {}))      # paleta da marca; sem ela, neutros
    CT = S["cartoes"]
    GRAIN = ("background-image: repeating-radial-gradient(circle at 17% 32%, rgba(255,255,255,.03) 0 1px, transparent 1px 3px),"
             " repeating-radial-gradient(circle at 73% 61%, rgba(0,0,0,.035) 0 1px, transparent 1px 4px);") if CT.get("grao") else ""
    bw = CX["largura"] * 1080; bh = bw / CX["proporcao"]; k = bw / 713.0
    box_bottom = CX["topo"] + bh / 1920
    def cartao(it):
        m = it["modelo"]
        if m == "pedra":
            return (f'<div class="cx-in" style="background:{PAL["pedra"]};align-items:center;justify-content:center;"><div class="cx-grao" style="{GRAIN}"></div>'
                    f'<div style="position:relative;width:74%;text-align:center;color:{PAL["texto_escuro"]};font-size:{CT["tamanho_frase_px"]*k:.0f}px;line-height:1.04;">{esc(it["texto"])}</div></div>')
        if m == "carvao":
            dest = f'<span style="font-style:italic;">{esc(it["destaque"])}</span><br>' if it.get("destaque") else ""
            return (f'<div class="cx-in" style="background:radial-gradient(130% 150% at 30% 20%, #4A4540 0%, #2E2B27 55%, #1E1C1A 100%);'
                    f'align-items:center;justify-content:center;"><div class="cx-grao" style="{GRAIN}"></div>'
                    f'<div style="position:relative;width:84%;text-align:center;color:{PAL["texto_claro"]};font-size:{CT["tamanho_destaque_px"]*k*0.72:.0f}px;line-height:0.98;">'
                    f'<span style="font-size:1.4em;">{dest}</span>{esc(it["texto"])}</div></div>')
        # papel: título no alto + traço + itens
        itens = "".join(f'<div>{esc(x)}</div>' for x in it.get("itens", []))
        return (f'<div class="cx-in" style="background:{PAL["papel"]};flex-direction:column;justify-content:space-between;padding:{36*k:.0f}px {44*k:.0f}px;">'
                f'<div class="cx-grao" style="{GRAIN}"></div><div style="position:relative;">'
                f'<div style="color:{PAL["texto_escuro"]};font-size:{CT["tamanho_titulo_px"]*k:.0f}px;line-height:0.98;">{esc(it["titulo"])}</div>'
                f'<div style="margin-top:{14*k:.0f}px;width:{90*k:.0f}px;height:{3*k:.1f}px;background:{PAL["taupe"]};"></div></div>'
                f'<div style="position:relative;display:flex;justify-content:space-between;color:#4A443D;font-style:italic;font-size:{32*k:.0f}px;">{itens}</div></div>')
    for n, it in enumerate(E["caixa_topo"]):
        a, b = it["de"], it["ate"]
        inner = (f'<div class="cx-in"><img src="assets/{it["arquivo"]}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
                 if it["tipo"] == "imagem" else cartao(it))
        add(f'<div id="cx{n}" class="clip" data-start="{r3(a)}" data-duration="{r3(b-a)}" data-track-index="3">'
            f'<div class="cx" style="left:{(1-CX["largura"])/2*100:.2f}%;top:{CX["topo"]*100:.2f}%;width:{CX["largura"]*100:.2f}%;height:{bh/1920*100:.2f}%;'
            f'border-radius:{CX["raio_px"]}px;">{inner}</div></div>')
        ftop, _ = face_span(a, b)
        if ftop < box_bottom + GAP:     # opção B: o motor não desloca o vídeo, só avisa
            print(f"⚠️  caixa do topo {a:.2f}–{b:.2f}: topo da cabeça a {ftop*100:.0f}% (caixa termina a {box_bottom*100:.0f}%). Regravar com mais espaço acima da cabeça.")
    # topo nunca vazio depois do título
    t0 = (T["ate"] if T else 0); itens = sorted((it["de"], it["ate"]) for it in E["caixa_topo"])
    furos = [(x1, y0) for (_, x1), (y0, _) in zip(itens, itens[1:]) if y0 - x1 > 0.05]
    if itens and itens[0][0] - t0 > 0.05: furos.insert(0, (t0, itens[0][0]))
    if itens and D - itens[-1][1] > 0.05: furos.append((itens[-1][1], D))
    for x, y in furos:
        print(f"⚠️  caixa do topo vazia de {x:.2f} a {y:.2f} (o padrão pede o topo sempre ocupado)")

import re
LIG = r"(?i)\b(pra|para|de|do|da|dos|das|que|e|o|a|os|as|um|uma|no|na|nos|nas|com|em|por|se|eu|the|to|of|and|in)\s+"
def cap_html(txt):
    h = esc(txt)
    # palavra de ligação presa à seguinte (espaço inseparável): nunca fica sozinha no fim de uma linha
    return re.sub(LIG, lambda m: m.group(1) + "&nbsp;", h) if CAP.get("prender_ligacao") else h

for n, (a, b, txt, up, low) in enumerate(caps):
    ht = header_top(a, b)
    top = ht if ht is not None else place(a, b, CAP_H, (CAP["posicao_fundo_mesclado"] if low else CAP["posicao"]) - CAP_H / 2)
    add(f'<div id="cap{n}" class="clip cap" data-start="{a}" data-duration="{r3(b-a)}" data-track-index="6">'
        f'<div class="cap-txt" style="top:{(top + CAP_H / 2)*100:.2f}%">{cap_html(txt)}</div></div>')

KS = KW["saida"]
for n, (a, b, k) in enumerate(kws):
    cid = f"kw{n}"
    rows = []
    seen_main = False
    for texto, papel, ids in k["partes"]:
        tokens = texto.split()
        main = papel == "principal"
        stack = main and len(texto) > KW["empilhar_acima_de_caracteres"]
        spans = []
        for wi, tok in zip(ids if len(ids) == len(tokens) else [ids[0]] * len(tokens), tokens):
            spans.append(f'<span class="w" data-t="{r3(W[wi]["s"])}">{esc(tok)}</span>')
        if stack:
            for s in spans:
                rows.append(f'<div class="kw-row kw-main">{s}</div>')
        else:
            align = "" if main else (" kw-after\" data-layout-allow-overflow=\"" if seen_main else " kw-before")
            rows.append(f'<div class="kw-row {"kw-main" if main else "kw-small"}{align}">{" ".join(spans)}</div>')
        seen_main = seen_main or main
    kh = sum(KW["altura_linha_principal"] if 'kw-main' in r else KW["altura_linha_pequena"] for r in rows)   # altura aproximada
    kt = place(a, b, kh, KW["posicao_fundo_mesclado"] if overlaps(a, b, topo_win) else KW["posicao"])
    neg = " kw-neg" if k.get("efeito") == "negativo" else ""      # PLAYBOOK 3.1 — variação opcional
    add(f'<div id="{cid}" class="clip kw{neg}" data-start="{r3(a)}" data-duration="{r3(b-a)}" data-track-index="7">'
        f'<div class="kw-block" style="top:{kt*100:.2f}%">{"".join(rows)}</div></div>')
    tl.append(f'kwWords("#{cid}"); tl.to("#{cid} .kw-block", {{opacity: 0, filter: "blur({KS["desfoque_px"]}px)", duration: {KS["duracao"]}}}, {r3(b-KS["duracao"])});')

for a, b in ZOOM["trechos"]:
    tl.append(f'tl.set(".cam", {{scale: {ZOOM["escala"]}}}, {a}); tl.set(".cam", {{scale: 1}}, {b});')

L, LG = M["logo"], S["logo"]
USA_LOGO = P.p.get("logo", LG.get("padrao", True))
if USA_LOGO:
    add(f'<img id="logo" class="logo" src="assets/img/logo-escuro.png" alt="" style="opacity:{L["opacidade"]}">')
    add('<img id="logo-claro" class="logo" src="assets/img/logo-claro.png" alt="" style="opacity:0">')

# Logo legível: sobre imagem de topo escura no canto do logo, troca pra versão clara
for t in (E["topo_mesclado"] if USA_LOGO else []):
    k = len(t["imagens"]); step = (t["ate"] - t["de"]) / k
    for m, img in enumerate(t["imagens"]):
        im = cv2.imread(os.path.join(P.assets, img), cv2.IMREAD_GRAYSCALE)
        h, w = im.shape
        if float(im[int(h * .05):int(h * .25), int(w * .65):].mean()) < LG["limiar_fundo_escuro"]:
            a, b = t["de"] + m * step, t["de"] + (m + 1) * step
            tl.append(f'tl.set("#logo", {{opacity: 0}}, {r3(a)}); tl.set("#logo-claro", {{opacity: {LG["opacidade_clara"]}}}, {r3(a)});'
                      f' tl.set("#logo", {{opacity: {L["opacidade"]}}}, {r3(b)}); tl.set("#logo-claro", {{opacity: 0}}, {r3(b)});')

KE = KW["entrada"]
page = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{esc(P.p.get("titulo", os.path.basename(P.dir)))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Padrao"; src: url("assets/fonts/{FONT_FILE}") format("truetype"); font-weight: {FW_RANGE}; }}
{CARD_FACES}
body {{ margin: 0; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "Padrao", sans-serif; font-weight: {FW}; color: {S["cor_texto"]}; }}
.clip {{ position: absolute; inset: 0; }}
.cam {{ position: absolute; inset: 0; transform-origin: {ZOOM["origem"]}; }}
.cam video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
/* PLAYBOOK 4.1–4.2 — cards */
.card-slot {{ display: flex; justify-content: center; }}
.card {{ position: absolute; top: 54%; overflow: hidden; border-radius: {CARD["raio_px"]}px; box-shadow: {CARD["sombra"]}; }}
.card img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.card.card {{ width: {CARD["largura"]*100:g}%; height: {CARD["altura"]*100:g}%; }}
.card.card-pequeno {{ width: {CARD["largura_pequeno"]*100:g}%; height: {CARD["altura_pequeno"]*100:g}%; }}
.card.noticia {{ width: {CARD["largura"]*100:g}%; height: auto; max-height: {CARD["altura_noticia_max"]*100:g}%; background: #fff; border-radius: {CARD["raio_noticia_px"]}px; }}
.card.noticia img {{ height: auto; object-fit: contain; }}
/* PLAYBOOK §1 — título de abertura */
.titulo {{ display: flex; justify-content: center; }}
.t-block {{ position: absolute; width: 90%; text-align: center; text-shadow: {TIT["sombra"]}; }}
.t-line {{ font-size: {TIT["tamanho_px"]}px; line-height: {TIT["entrelinha"]}; letter-spacing: {TIT["espacamento"]}; }}
.t-sub {{ font-size: {TIT.get("subtitulo_px", 34)}px; margin-top: 10px; opacity: .95; }}
/* PLAYBOOK §3 — legenda */
.cap {{ display: flex; justify-content: center; }}
.cap-txt {{ position: absolute; transform: translateY(-50%); width: {CAP["largura"]}; text-align: center; font-size: {CAP["tamanho_px"]}px;
  font-weight: {CAP.get("peso", FW)}; line-height: {CAP["entrelinha"]}; letter-spacing: {CAP["espacamento"]}; text-shadow: {CAP["sombra"]};
  {"text-wrap: balance;" if CAP.get("equilibrar_linhas") else ""} }}
/* PLAYBOOK 3.1 — palavras-chave */
.kw {{ display: flex; justify-content: center; }}
.kw-block {{ position: absolute; display: flex; flex-direction: column; align-items: center; text-shadow: {KW["sombra"]}; }}
.kw-row {{ white-space: nowrap; }}
.kw-small {{ font-size: {KW["pequena_px"]}px; letter-spacing: {KW["espacamento_pequena"]}; line-height: 1.0; }}
.kw-main {{ font-size: 200px; letter-spacing: {KW["espacamento_principal"]}; line-height: 0.86; }}
.w {{ display: inline-block; }}
/* PLAYBOOK 3.1 — efeito negativo: as letras invertem as cores do vídeo atrás delas */
.kw-neg .kw-block {{ mix-blend-mode: difference; text-shadow: none; }}
.cx {{ position: absolute; overflow: hidden; }}
.cx-in {{ position: absolute; inset: 0; display: flex; font-family: "Cartao", serif; overflow: hidden; }}
.cx-grao {{ position: absolute; inset: 0; }}
.logo {{ position: absolute; top: {LG["topo"]}; right: {LG["direita"]}; width: {LG["largura"]}; height: auto; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{D}">
{chr(10).join(out)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
function fitTitle() {{
  // Gancho (topo-livre): tamanho FIXO pela altura das letras; cada linha a uma distância fixa da anterior;
  // subtítulo colado embaixo da última linha. Só encolhe se uma linha passar da largura da tela.
  const H = 1920;
  const ink = (el) => {{
    const cs = getComputedStyle(el);
    ctx.font = `${{cs.fontWeight}} ${{parseFloat(cs.fontSize)}}px Padrao`;
    const m = ctx.measureText(el.textContent.trim());
    return {{ fa: m.fontBoundingBoxAscent, ia: m.actualBoundingBoxAscent }};
  }};
  document.querySelectorAll(".titulo").forEach((box) => {{
    const lines = [...box.querySelectorAll(".t-fit")];
    if (!lines.length) return;
    const t0 = lines[0];
    ctx.font = `${{getComputedStyle(t0).fontWeight}} 100px Padrao`;
    const capH = ctx.measureText("H").actualBoundingBoxAscent;
    let fs = 100 * parseFloat(t0.dataset.letras) * H / capH;
    const maxW = parseFloat(t0.dataset.alvo) * 1080;
    lines.forEach((l) => {{ l.style.lineHeight = "normal"; l.style.fontSize = fs + "px"; }});
    const widest = Math.max(...lines.map((l) => l.scrollWidth));
    if (widest > maxW) {{ fs = fs * maxW / widest; lines.forEach((l) => (l.style.fontSize = fs + "px")); }}
    const cap = parseFloat(t0.dataset.letras) * H * (fs / (100 * parseFloat(t0.dataset.letras) * H / capH));
    const passo = cap * parseFloat(t0.dataset.entre);
    let inkTop = parseFloat(t0.dataset.topo) * H, lastBottom = 0;
    lines.forEach((l, i) => {{
      const k = ink(l), top = inkTop + i * passo;
      l.style.top = (top - (k.fa - k.ia)) + "px";
      lastBottom = top + k.ia;
    }});
    const s = box.querySelector(".t-fit-sub");
    if (s) {{
      s.style.lineHeight = "normal"; s.style.fontSize = "100px";
      s.style.fontSize = (100 * parseFloat(s.dataset.alvo) * 1080 / s.scrollWidth) + "px";
      const ks = ink(s);
      s.style.top = (lastBottom + parseFloat(s.dataset.folga) * H - (ks.fa - ks.ia)) + "px";
    }}
  }});
}}
function fitMain() {{
  // palavra principal: tamanho pela largura alvo, entre o mínimo e o máximo do padrão (PLAYBOOK 3.1)
  document.querySelectorAll(".kw-block").forEach((b) => {{
    const rows = b.querySelectorAll(".kw-main");
    let widest = 0;
    rows.forEach((r) => {{ r.style.fontSize = "100px"; widest = Math.max(widest, r.scrollWidth); }});
    const size = Math.max({KW["principal_min_px"]}, Math.min({KW["principal_max_px"]}, Math.floor(100 * {KW["largura_alvo_px"]} / widest)));
    rows.forEach((r) => (r.style.fontSize = size + "px"));
    tighten(b, size);
    anchor(b, size);
  }});
}}
// Ancora as palavras pequenas na palavra grande (não na largura do bloco), como nas referências:
// antes → encaixadas no canto superior esquerdo da 1ª linha grande ("Do it / yourself");
// depois → no canto inferior direito da última linha grande ("days / ...forget."), podendo passar dela.
function anchor(block, size) {{
  const mains = [...block.querySelectorAll(".kw-main")];
  const widest = Math.max(...mains.map((r) => r.offsetWidth));
  block.style.width = widest + "px";           // a largura do bloco é a da palavra grande
  const first = mains[0], last = mains[mains.length - 1];
  const nudge = Math.round(size * 0.02);       // compensa o respiro lateral da letra grande
  block.querySelectorAll(".kw-before").forEach((r) => {{
    r.style.alignSelf = "flex-start";
    r.style.marginLeft = ((widest - first.offsetWidth) / 2 + nudge) + "px";
  }});
  block.querySelectorAll(".kw-after").forEach((r) => {{
    if (r.offsetWidth > last.offsetWidth) {{
      // mais larga que a palavra grande: começa no "pé" esquerdo dela e cresce pra direita (ordem de leitura)
      r.style.alignSelf = "flex-start";
      r.style.marginLeft = ((widest - last.offsetWidth) / 2 + nudge) + "px";
    }} else {{
      r.style.alignSelf = "flex-end";
      r.style.marginRight = ((widest - last.offsetWidth) / 2 + nudge) + "px";
    }}
  }});
}}
// Encosta as linhas pelo contorno real das letras (sem o espaço vazio que a fonte reserva acima/abaixo).
const ctx = document.createElement("canvas").getContext("2d");
function inkBox(row) {{
  const fs = parseFloat(getComputedStyle(row).fontSize);
  ctx.font = `{FW} ${{fs}}px Padrao`;
  const m = ctx.measureText(row.textContent.trim());
  return {{ fs, fontAsc: m.fontBoundingBoxAscent, fontDesc: m.fontBoundingBoxDescent,
           inkAsc: m.actualBoundingBoxAscent, inkDesc: m.actualBoundingBoxDescent }};
}}
function tighten(block, mainSize) {{
  const gap = Math.round(mainSize * {KW["folga"]});
  block.querySelectorAll(".kw-row").forEach((row) => {{
    const k = inkBox(row);
    row.style.lineHeight = "normal";
    const top = -(k.fontAsc - k.inkAsc);
    const bottom = -(k.fontDesc - k.inkDesc);
    let mt = row === block.firstElementChild ? top : top + gap;
    // Encaixe no vão (PLAYBOOK 3.1): a linha pequena de antes desce até o topo das letras BAIXAS iniciais
    // da palavra grande, quando cabe ali ("um" sobre o "v" de "vilão", colado no pingo do "i").
    const prev = row.previousElementSibling;
    if (row.classList.contains("kw-main") && prev && prev.classList.contains("kw-before")) {{
      const txt = row.textContent.trim();
      ctx.font = `{FW} ${{k.fs}}px Padrao`;
      const xAsc = ctx.measureText("x").actualBoundingBoxAscent;
      let run = "";
      for (const ch of txt) {{
        if (ctx.measureText(ch).actualBoundingBoxAscent > xAsc * 1.06) break;   // letra alta, acento, pingo ou maiúscula
        run += ch;
      }}
      const notch = run ? ctx.measureText(run).width : 0;
      if (notch > 0 && prev.offsetWidth <= notch * 0.98) {{
        const runAsc = ctx.measureText(run).actualBoundingBoxAscent;
        mt -= (k.inkAsc - runAsc);
      }}
    }}
    row.style.marginTop = mt + "px";
    row.style.marginBottom = bottom + "px";
  }});
}}
function kwWords(sel) {{
  document.querySelectorAll(sel + " .w").forEach((w) => {{
    tl.fromTo(w, {{ opacity: 0, y: {KE["sobe_px"]}, filter: "blur({KE["desfoque_px"]}px)" }},
      {{ opacity: 1, y: 0, filter: "blur(0px)", duration: {KE["duracao"]}, ease: "power2.out" }}, parseFloat(w.dataset.t));
  }});
}}
document.fonts.ready.then(() => {{
  fitMain();
  fitTitle();
  tl.set(".cam", {{ scale: 1 }}, 0);
  {(chr(10) + "  ").join(tl)}
  window.__timelines["main"] = tl;
}});
</script>
</body>
</html>
"""
open(P.path("composicao/index.html"), "w", encoding="utf-8").write(page)
print(f"index.html gerado ({S['nome']} v{S['versao']} / marca {M['nome']}): {len(caps)} legendas, {len(kws)} palavras-chave, "
      f"{len(cards)} cards, {sum(len(t['imagens']) for t in E['topo_mesclado'])} imagens no fundo mesclado")
