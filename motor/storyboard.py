"""Storyboard: uma folha com um quadro por momento do vídeo, ANTES da edição completa (vale pra todo padrão).

Cada quadro é a composição real do motor (gerar.py) naquele instante — vídeo do A-roll com cortes, aceleração e cor,
mais caixa/cartões/título/legendas/palavras-chave nas posições do padrão — com, embaixo: tempo, fala exata,
tipo da inserção, origem da imagem e ALERTAS de regra (rosto coberto, limites de caracteres, caixa vazia...).

Pré-requisitos: composicao/assets/aroll.mp4 (motor/cortes.py), transcricao/aroll.words.json, edicao.json.
O recorte completo NÃO é necessário: sem cache/rosto.json, usa o mapa rápido (rosto.py --rapido).

Uso: python motor/storyboard.py projetos/<video>   → projetos/<video>/storyboard/storyboard.jpg
"""
import html, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

AQUI = os.path.dirname(os.path.abspath(__file__))
P = Projeto(sys.argv[1]); E = P.edicao(); S = P.S
W = json.load(open(P.path("transcricao/aroll.words.json"), encoding="utf-8"))
OUT = P.path("storyboard"); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
PY = [sys.executable, "-I"]
esc = html.escape

# 1. mapa do rosto (rápido, se o completo ainda não existe)
if not os.path.exists(P.path("cache/rosto.json")) and not os.path.exists(P.path("cache/rosto_rapido.json")):
    os.makedirs(P.path("cache"), exist_ok=True)
    print("mapa rápido do rosto…")
    subprocess.run(PY + [os.path.join(AQUI, "rosto.py"), os.path.join(P.assets, "aroll.mp4"), "--rapido",
                         P.path("cache/rosto_rapido.json")], check=True, capture_output=True)

# 2. composição real + avisos do gerador
g = subprocess.run(PY + [os.path.join(AQUI, "gerar.py"), P.dir], capture_output=True, text=True)
if g.returncode:
    sys.exit(g.stderr)
avisos = [l.strip() for l in g.stdout.splitlines() if "⚠️" in l]

def avisos_em(a, b):
    out = []
    for l in avisos:
        m = re.search(r"(\d+\.\d+)[–-](\d+\.\d+)", l)
        if not m or (float(m.group(1)) < b and float(m.group(2)) > a):
            out.append(l.replace("⚠️", "").strip())
    return out

def fala(a, b):
    # texto revisado das legendas (o do Whisper pode ter palavras erradas); sem legenda, cai na transcrição
    caps = [t for t, i, j in E.get("legendas", []) if W[i]["s"] < b and W[j]["e"] > a]
    return " / ".join(caps) if caps else " ".join(w["w"] for w in W if w["s"] < b and w["e"] > a)

origens = {}
op = P.path("insercoes/ORIGEM.md")
if os.path.exists(op):
    for linha in open(op, encoding="utf-8"):
        c = [x.strip() for x in linha.split("|")]
        if len(c) > 3 and "." in c[1]:
            origens[c[1]] = c[3]

# 3. momentos: tudo que entra na tela, em ordem
mom = []
T = E.get("titulo")
if T:
    mom.append((T["de"], T["ate"], "Gancho", f'título "{" ".join(T["linhas"])}" ({len(" ".join(T["linhas"]))} car.)'
                + (f' · subtítulo ({len(T.get("subtitulo", ""))} car.)' if T.get("subtitulo") else "")
                + (f' · colagem: {", ".join(os.path.basename(x) for x in T.get("colagem", []))}' if T.get("colagem") else ""), ""))
for it in E.get("caixa_topo", []):
    if it["tipo"] == "imagem":
        nome = os.path.basename(it["arquivo"])
        mom.append((it["de"], it["ate"], "Caixa · imagem", nome, origens.get(nome, it.get("origem", ""))))
    else:
        txt = it.get("texto") or it.get("titulo", "")
        mom.append((it["de"], it["ate"], f'Caixa · cartão {it["modelo"]}', f'"{(it.get("destaque", "") + " " + txt).strip()}"', ""))
for c in E.get("cards", []):
    mom.append((c["de"], c["ate"], f'Card · {c["tipo"]}', os.path.basename(c["arquivo"]), origens.get(os.path.basename(c["arquivo"]), "")))
for t in E.get("topo_mesclado", []):
    mom.append((t["de"], t["ate"], "Fundo mesclado", ", ".join(os.path.basename(x) for x in t["imagens"]), ""))
for a in E.get("texto_atras", []):
    mom.append((a["de"], a["ate"], "Texto atrás", f'"{a["texto"]}"', ""))
for k in E.get("palavras_chave", []):
    ids = [i for _, _, x in k["partes"] for i in x]
    a, b = W[min(ids)]["s"], W[max(ids)]["e"] + k.get("segura", 0)
    mom.append((a, b, "Palavra-chave" + (" · negativo" if k.get("efeito") == "negativo" else ""),
                " / ".join(p[0] for p in k["partes"]), ""))
if not mom:   # vídeo só com legendas: um quadro a cada ~4 s
    d = E["duracao"]; mom = [(x, min(d, x + 4), "Legenda", "", "") for x in range(0, int(d), 4)]
mom.sort()

# 4. quadros reais da composição
tempos = [round(min(b - 0.05, a + max(0.35, (b - a) * 0.4)), 2) for a, b, *_ in mom]
subprocess.run(["npx", "--yes", "hyperframes@0.8.150", "snapshot", "--at", ",".join(map(str, tempos)), "--no-end",
                "--describe", "false", "-o", os.path.join(OUT, "q"), "--timeout", "20000"],
               cwd=P.path("composicao"), capture_output=True, check=True)
pngs = sorted(f for f in os.listdir(os.path.join(OUT, "q")) if f.startswith("frame-"))

# 5. folha
cards = []
for n, ((a, b, tipo, det, orig), png) in enumerate(zip(mom, pngs)):
    al = avisos_em(a, b)
    alert = "".join(f'<div class="al">⚠ {esc(x)}</div>' for x in al)
    cards.append(f'''<div class="q{' tem-alerta' if al else ''}"><img src="q/{png}"><div class="info">
<div class="n">{n+1}<span>{a:.1f}–{b:.1f} s · {b-a:.1f} s</span></div>
<div class="tp">{esc(tipo)}</div><div class="det">{esc(det)}</div>
<div class="fala">“{esc(fala(a, b))}”</div>{f'<div class="or">origem: {esc(orig)}</div>' if orig else ''}{alert}</div></div>''')
COLS = 4
linhas = (len(cards) + COLS - 1) // COLS
alto = 2 * (linhas * 1010 + 160)
geral = "".join(f"<li>{esc(x.replace('⚠️', '').strip())}</li>" for x in avisos)
page = f"""<!doctype html><html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
body{{margin:0;background:#141414;font-family:-apple-system,Helvetica,sans-serif;color:#eee}}
#root{{position:relative;width:100%;height:100%;padding:36px;box-sizing:border-box;}}
h1{{margin:0 0 6px;font-size:40px}} .sub{{color:#aaa;font-size:24px;margin-bottom:24px}}
.grid{{display:grid;grid-template-columns:repeat({COLS},1fr);gap:28px}}
.q{{background:#1f1f1f;border:2px solid #2c2c2c;border-radius:10px;overflow:hidden}}
.q.tem-alerta{{border-color:#e5484d}}
.q img{{width:100%;display:block}}
.info{{padding:14px 16px 18px;font-size:21px;line-height:1.35}}
.n{{font-size:34px;font-weight:700}} .n span{{font-size:20px;font-weight:400;color:#aaa;margin-left:10px}}
.tp{{color:#f5d76e;font-weight:600;margin-top:4px}} .det{{color:#ddd}} .fala{{color:#9ad;margin-top:6px;font-style:italic}}
.or{{color:#888;font-size:18px;margin-top:4px;word-break:break-all}} .al{{color:#ff6b6b;font-weight:600;margin-top:8px}}
ul{{color:#ff6b6b;font-size:22px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="2400" data-height="{alto}" data-duration="1">
<h1>Storyboard — {esc(P.p.get("titulo", os.path.basename(P.dir)))}</h1>
<div class="sub">padrão {S["nome"]} v{S["versao"]} · marca {esc(P.M["nome"])} · {E["duracao"]:.1f} s · {len(cards)} momentos
 · aceleração {P.p.get("aceleracao")}× · cor: {P.p.get("grading") or "original"}</div>
{f"<ul>{geral}</ul>" if geral else ""}
<div class="grid">{"".join(cards)}</div></div>
<script>window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
subprocess.run(["npx", "--yes", "hyperframes@0.8.150", "snapshot", ".", "--at", "0.5", "--no-end", "--describe", "false",
                "-o", "folha", "--timeout", "20000"], cwd=OUT, capture_output=True, check=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(OUT, "folha", "frame-00-at-0.5s.png"),
                "-vf", "scale=1600:-2", "-q:v", "3", os.path.join(OUT, "storyboard.jpg")], check=True)
shutil.rmtree(os.path.join(OUT, "folha"))
print(f"storyboard: {len(cards)} momentos, {len(avisos)} alerta(s) → {os.path.join(OUT, 'storyboard.jpg')}")
