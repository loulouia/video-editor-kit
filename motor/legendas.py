"""Divide a fala em legendas respeitando o padrão: no máximo `linhas_max` linhas de `caracteres_por_linha`
e no máximo `palavras_max` palavras por tela (se o padrão definir)
(PLAYBOOK §4 de cada padrão). Prefere quebrar em pontuação; nunca deixa uma palavra sozinha no fim.

Padrão com "palavras_por_linha" (ex.: basico): monta linhas explícitas (até `palavras_por_linha` palavras, até
`linhas_max` linhas) e escolhe as palavras de destaque (`legenda.destaque`): pelo menos uma a cada
`intervalo_max_s`, de preferência números e palavras fortes, alternando destaque sozinho numa linha e junto.
Cada legenda vira [texto, i, j, {"linhas": [[índices]...], "destaques": [índices], "sozinha": [índices]}].
O Claude revisa os destaques no plano (trocar por palavras mais importantes do sentido) antes de gravar.

Uso: python motor/legendas.py projetos/<video> [--de <indice> --ate <indice>] [--destaques 15,16;43,44] [--gravar]
     --destaques: os destaques escolhidos na revisão (grupos de 1–2 índices de palavras, separados por ";");
                  as linhas são montadas em volta deles (padrões com "palavras_por_linha")
     Lê transcricao/aroll.words.json e imprime as legendas; com --gravar, escreve em edicao.json → "legendas"
     (formato [texto, índice_da_primeira_palavra, índice_da_última]). Revisar a grafia pelo glossário da marca
     antes de gravar: o texto vem do Whisper.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Projeto

P = Projeto(sys.argv[1])
L = P.S["legenda"]
MAXC = L.get("caracteres_por_linha", 30) * L.get("linhas_max", 2)
PMAX = L.get("palavras_max", 99)  # palavras por tela (padrão amanda: 5)
ALVO = int(MAXC * 0.88)          # mira abaixo do máximo (na referência, a maioria fica entre 25 e 55 caracteres)
# palavras de ligação: uma legenda nunca termina nelas (vão pra legenda seguinte)
LIGACAO = {"pra", "para", "de", "do", "da", "dos", "das", "que", "e", "o", "a", "os", "as", "um", "uma",
           "no", "na", "nos", "nas", "com", "em", "por", "se", "eu", "você", "the", "a", "to", "of", "and", "in"}
W = json.load(open(P.path("transcricao/aroll.words.json"), encoding="utf-8"))
a = int(sys.argv[sys.argv.index("--de") + 1]) if "--de" in sys.argv else 0
b = int(sys.argv[sys.argv.index("--ate") + 1]) if "--ate" in sys.argv else len(W) - 1

def fmt(ws):
    t = " ".join(w["w"] for w in ws).strip()
    if L.get("minusculas"):          # tudo em minúsculas (padrão amanda v1.1)
        return t.lower()
    return t.upper() if L.get("maiusculas", True) else t[:1].lower() + t[1:] if t[:2] != t[:2].upper() else t

PPL = L.get("palavras_por_linha")
# legenda em blocos/linhas (palavra por palavra): lista de ligação mais completa (não muda a divisão dos outros padrões)
LIGACAO_PP = LIGACAO | {"ao", "aos", "à", "às", "pelo", "pela", "pelos", "pelas", "num", "numa", "mas", "ou", "nem",
                        "nesse", "nessa", "neste", "nesta", "seu", "sua", "meu", "minha", "te", "me", "lhe"}
DEST = L.get("destaque") or {}


def limpa(k):
    return W[k]["w"].strip().strip(",.?!;:\"'…").lower()


# palavras que não carregam sentido sozinhas: nunca viram destaque automático
FRACAS = {"vamos", "vai", "vou", "tinha", "tem", "ter", "isso", "isto", "esse", "essa", "este", "esta", "está", "estão",
          "ela", "ele", "elas", "eles", "você", "vocês", "gente", "muito", "muita", "mais", "menos", "será", "talvez",
          "aqui", "então", "porque", "quando", "como", "também", "ainda", "sempre", "nunca", "agora", "depois", "antes",
          "sobre", "entre", "mesmo", "mesma", "outro", "outra", "todo", "toda", "tudo", "cada", "qual", "quem", "onde",
          "pode", "podem", "fazer", "feito", "falar", "dentro", "fora", "coisa", "coisas", "lado", "sido", "estar", "fica", "ficar", "acho", "assim", "nessa", "nesse", "desse",
          "dessa", "daqui", "disso", "dela", "dele", "seu", "sua", "seus", "suas", "meu", "minha", "nosso", "nossa",
          "enquanto", "simplesmente", "serve", "seja", "aí", "sim", "vez", "vezes",
          "were", "that", "this", "with", "have", "they", "what", "just", "really", "about", "there"}


def forca(k):
    """Quanto a palavra serve de destaque: números, nomes próprios, depois palavras longas; vazias nunca."""
    t = limpa(k)
    if not t or t in LIGACAO_PP or t in FRACAS:
        return 0
    if any(c.isdigit() for c in t):
        return 100
    bruta = W[k]["w"].strip()
    inicio_frase = k == 0 or W[k - 1]["w"].strip()[-1:] in ".?!"
    if bruta[:1].isupper() and not inicio_frase:
        return 50 + len(t)
    return len(t) if len(t) >= 5 else 1


def escolher_destaques(a, b):
    """Um destaque a cada intervalo_min..intervalo_max segundos (nunca mais que intervalo_max sem nenhum)."""
    if not DEST:
        return []
    mn, mx = DEST.get("intervalo_min_s", 2.5), DEST.get("intervalo_max_s", 4.0)
    out, last, i = [], W[a]["s"] - mn, a
    while i <= b:
        janela = [k for k in range(i, b + 1) if last + mn <= W[k]["s"] <= last + mx]
        if not janela:      # pausa longa: as primeiras palavras depois dela
            depois = [k for k in range(i, b + 1) if W[k]["s"] > last + mx]
            if not depois:
                break
            janela = [k for k in depois if W[k]["s"] <= W[depois[0]]["s"] + (mx - mn)]
        k = max(janela, key=lambda k: (forca(k), -k))
        if forca(k) <= 1:   # nada forte no intervalo: espera até ~2 s a mais por uma palavra boa (nunca destaca "e", "isso")
            adiante = [x for x in range(janela[-1] + 1, b + 1) if W[x]["s"] <= W[janela[-1]]["s"] + 2.0 and forca(x) > 1]
            if adiante:
                k = max(adiante, key=lambda x: (forca(x), -x))
            elif forca(k) == 0:
                i = janela[-1] + 1
                continue
        out.append(k)
        last, i = W[k]["s"], k + 1
    return out


# palavra antes do destaque que forma expressão com ele ("não tem", "de volume", "das mamas", "sem nada")
PREFIXO = {"não", "sem", "de", "da", "do", "das", "dos", "um", "uma", "mais", "muito", "tão", "bem", "nunca",
           "o", "a", "os", "as", "no", "na", "nos", "nas", "seu", "sua", "nossa", "nosso"}


def grupos_destaque(a, b):
    """Cada destaque: a palavra forte e, se o padrão permitir 2 palavras, a anterior quando forma expressão com ela.
    Com --destaques, usa os grupos escolhidos na revisão."""
    if "--destaques" in sys.argv:
        txt_g = sys.argv[sys.argv.index("--destaques") + 1]
        return [[int(x) for x in g.split(",")] for g in txt_g.split(";") if g.strip()]
    grupos, usados = [], set()
    for k in escolher_destaques(a, b):
        g = [k]
        if DEST.get("ate_palavras", 1) >= 2 and k - 1 >= a and k - 1 not in usados and limpa(k - 1) in PREFIXO \
                and W[k - 1]["w"].strip()[-1:] not in ".?!,;:":
            g = [k - 1, k]
        grupos.append(g); usados.update(g)
    return grupos


def por_linhas(a, b):
    grupos = grupos_destaque(a, b)
    inicio = {g[0]: g for g in grupos}
    dest = {k for g in grupos for k in g}
    pular = set()
    ESC = DEST.get("escala", 1)
    alterna = DEST.get("alternar_sozinha")
    vez_sozinha = True          # alterna: sozinha, junto, sozinha...
    soz = set()
    MAXL = L.get("caracteres_por_linha", 99)
    LMAX = L.get("linhas_max", 2)
    caps, linhas, linha = [], [], []

    def txt(ks):     # largura aproximada em caracteres (destaque conta maior)
        return "x" * round(sum(len(W[k]["w"].strip()) * (ESC if k in dest else 1) for k in ks) + len(ks) - 1)

    def fecha_linha():
        nonlocal linha
        if linha:
            linhas.append(linha)
        linha = []

    def fecha_legenda():
        nonlocal linhas
        fecha_linha()
        if linhas:
            caps.append(linhas)
        linhas = []

    for k in range(a, b + 1):
        if k in pular:
            continue
        if alterna and k in inicio:
            # linha atual só com palavras de ligação ("uma") → o destaque divide a linha com elas desta vez
            # ou linha terminando em ligação ("uma perda de") → também divide; a vez de ficar sozinha passa pro próximo
            # ou a legenda já tem uma linha e a atual está pela metade (sobraria um pedaço solto) → também divide
            bloqueia = bool(linha) and (all(limpa(x) in LIGACAO_PP for x in linha) or limpa(linha[-1]) in LIGACAO_PP
                                        or len(linhas) >= LMAX - 1)
            if vez_sozinha and not bloqueia:
                soz.add(k)
                vez_sozinha = False
            elif not vez_sozinha:
                vez_sozinha = True
        if k in soz:                              # destaque sozinho: uma linha só dele (1 ou 2 palavras)
            if linha and len(linhas) + 1 >= LMAX:
                fecha_legenda()
            fecha_linha()
            if len(linhas) >= LMAX:
                fecha_legenda()
            linhas.append(list(inicio[k]))
            pular.update(inicio[k][1:])
            k = inicio[k][-1]
        else:
            unid = list(inicio.get(k, [k]))       # destaque de 2 palavras junto: nunca separa as duas
            # largura passou mas a linha atual é só ligação ("em", "nos"): não deixa a palavrinha sozinha — segue
            # na linha e o gerar.py diminui o destaque pra caber (regra da linha larga)
            so_lig = bool(linha) and all(limpa(x) in LIGACAO_PP for x in linha)
            if linha and (len(linha) + len(unid) > PPL or (len(txt(linha + unid)) > MAXL and not so_lig)):
                carrega = []
                while len(linha) > 1 and limpa(linha[-1]) in LIGACAO_PP:   # ligação nunca no fim da linha
                    carrega.insert(0, linha.pop())
                if all(limpa(x) in LIGACAO_PP for x in linha) or len(carrega) >= PPL:   # sobraria só ligação: desiste
                    linha += carrega
                    carrega = []
                fecha_linha()
                if len(linhas) >= LMAX:
                    fecha_legenda()
                linha = carrega
            if not linha and len(linhas) >= LMAX:
                fecha_legenda()
            linha += unid
            pular.update(unid[1:])
            k = unid[-1]
        fim = W[k]["w"].strip()[-1:]
        n_pal = sum(len(x) for x in linhas) + len(linha)
        if fim in ".?!" and n_pal >= 1:          # fim de frase fecha a legenda
            fecha_legenda()
        elif fim in ",;:" and len(linha) >= 2:    # vírgula fecha a linha
            fecha_linha()
            if len(linhas) >= LMAX:
                fecha_legenda()
        elif not linha and len(linhas) >= LMAX:
            fecha_legenda()
    fecha_legenda()
    # legenda de 1 linha (estilo "simples"): fala rápida deixaria uma linha piscando na tela; redistribui as palavras
    # entre ela e a próxima (até `palavras_por_linha` cada), escolhendo o corte que deixa as duas mais tempo na tela
    TMIN = L.get("tempo_min_linha_s", 0.35)
    if LMAX == 1:
        soz_todas = {x for k in soz for x in inicio[k]}
        def dur(n):
            ini = W[caps[n][0][0]]["s"]
            fim = W[caps[n + 1][0][0]]["s"] if n + 1 < len(caps) else W[caps[n][-1][-1]]["e"] + 0.3
            return fim - ini
        def redistribuir(x, y, rigido, limite=PPL):
            """Junta as linhas x e y (seguidas) e corta de novo onde as duas ficam mais tempo na tela."""
            pool = caps[x][0] + caps[y][0]
            fim2 = W[caps[y + 1][0][0]]["s"] if y + 1 < len(caps) else W[pool[-1]]["e"] + 0.3
            melhor = None
            frase = not any(W[k]["w"].strip()[-1:] in ".?!" for k in pool[:-1])
            if len(pool) <= limite and (limite == PPL or len(txt(pool)) <= MAXL) and (frase or not rigido):   # junta
                melhor = (fim2 - W[pool[0]]["s"], pool, None)
            for c in range(1, len(pool)):
                p1, p2 = pool[:c], pool[c:]
                if len(p1) > PPL or len(p2) > PPL or any(g[0] in p1 and g[-1] in p2 for g in grupos):
                    continue
                if rigido and limpa(p1[-1]) in LIGACAO_PP and len(p1) > 1:
                    continue
                if rigido and any(W[k]["w"].strip()[-1:] in ".?!" for k in p1[:-1] + p2[:-1]):
                    continue                      # não junta o fim de uma frase com o começo da outra
                nota = min(W[p2[0]]["s"] - W[p1[0]]["s"], fim2 - W[p2[0]]["s"])
                if melhor is None or nota > melhor[0]:
                    melhor = (nota, p1, p2)
            return melhor
        n = 0
        while n < len(caps):
            if dur(n) < TMIN:
                pares = [(n, n + 1)] if n + 1 < len(caps) else []
                pares += [(n - 1, n)] if n > 0 else []
                # legível vem antes de "não terminar em ligação"; último recurso: uma linha de PPL+1 palavras
                # (fala rapidíssima, ex. "aqui é o lugar" em 0,3 s) — melhor que a palavra sumir da legenda
                for rigido, limite in ((True, PPL), (False, PPL), (False, PPL + 1)):
                    if limite > PPL and dur(n) >= 0.2:   # exceção só quando a palavra sumiria da legenda
                        break
                    feito = False
                    for x, y in pares:
                        if set(caps[x][0] + caps[y][0]) & soz_todas:
                            continue
                        m = redistribuir(x, y, rigido, limite)
                        if m and m[0] > dur(n) and m[0] >= 0.2:
                            if m[2] is None:
                                caps[x] = [m[1]]; del caps[y]
                            else:
                                caps[x], caps[y] = [m[1]], [m[2]]
                            feito = True
                            break
                    if feito:
                        break
            n += 1

    # legenda nunca termina em palavra de ligação: passa pra próxima
    for n in range(len(caps) - 1):
        ult = caps[n][-1]
        if len(ult) > 1 and limpa(ult[-1]) in LIGACAO_PP and ult[0] not in soz:
            k = ult.pop()
            prim = caps[n + 1][0]
            if len(prim) < PPL and prim[0] not in soz:
                prim.insert(0, k)
            else:
                caps[n + 1].insert(0, [k])
                if len(caps[n + 1]) > LMAX:          # não coube: devolve
                    caps[n + 1].pop(0); ult.append(k)
    saida = []
    for ls in caps:
        ks = [k for l in ls for k in l]
        t = fmt([W[k] for k in ks]).rstrip(",")
        orig = W[ks[0]]["w"].strip()
        meio_frase = ks[0] > 0 and W[ks[0] - 1]["w"].strip()[-1:] not in ".?!"
        if orig[:1].isupper() and meio_frase and not L.get("maiusculas", True):   # nome próprio no começo do bloco
            t = orig[:1] + t[1:]
        soz_todas = {x for k in soz for x in inicio[k]}
        saida.append([t, ks[0], ks[-1], {"linhas": ls, "destaques": [k for k in ks if k in dest],
                                         "sozinha": [k for k in ks if k in soz_todas]}])
    return saida


caps, cur = [], []
for i in (range(a, b + 1) if not PPL else ()):
    w = W[i]
    if cur and (len(fmt(cur + [w])) > ALVO or len(cur) + 1 > PMAX):   # não cabe: fecha a legenda atual
        cut = len(cur)
        # recua palavras de ligação do fim e a palavra solta depois de uma vírgula
        while cut > 2 and cur[cut - 1]["w"].lower().strip(",.") in LIGACAO:
            cut -= 1
        if cut == len(cur) and cut > 2 and cur[-2]["w"][-1] in ",;:" and cur[-1]["w"][-1] not in ".?!,":
            cut -= 1
        caps.append(cur[:cut]); cur = cur[cut:]
    cur.append(w)
    end = w["w"][-1]
    if end in ".?!" and len(fmt(cur)) >= 12:          # fim de frase fecha a legenda
        caps.append(cur); cur = []
    elif end in ",;:" and len(fmt(cur)) >= ALVO * 0.6: # vírgula depois de ~60% do limite também fecha
        caps.append(cur); cur = []
if cur:
    caps.append(cur)
# sobra curta (menos de 12 caracteres) junta na legenda anterior, se couber no máximo
k = 1
while k < len(caps):
    if len(fmt(caps[k])) < 12 and len(fmt(caps[k - 1] + caps[k])) <= MAXC and len(caps[k - 1] + caps[k]) <= PMAX:
        caps[k - 1] = caps[k - 1] + caps.pop(k)
    else:
        k += 1

idx = {id(w): k for k, w in enumerate(W)}
out = [[fmt(c).rstrip(","), idx[id(c[0])], idx[id(c[-1])]] for c in caps] if not PPL else por_linhas(a, b)
for t, i, j, *meta in out:
    if meta:
        toks = t.split()
        m = meta[0]
        mostra = " / ".join(" ".join((toks[k - i].upper() + ("(só)" if k in m["sozinha"] else "")) if k in m["destaques"]
                                     else toks[k - i] for k in l) for l in m["linhas"]) if len(toks) == j - i + 1 else t
        print(f"{W[i]['s']:6.2f}  {mostra}")
    else:
        print(f"{W[i]['s']:6.2f}  [{len(t):2d}] {t}")
if "--gravar" in sys.argv:
    e = P.edicao(); e["legendas"] = out
    import hashlib     # "impressão digital" do texto: o gerar.py recusa legendas montadas sobre outro texto
    e["legendas_texto"] = hashlib.sha1("\n".join(w["w"] for w in W).encode("utf-8")).hexdigest()[:12]
    json.dump(e, open(P.path("edicao.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(out)} legendas gravadas (máx. {MAXC} caracteres, {L.get('linhas_max', 2)} linha(s), {PMAX} palavras)"
          + (f", {sum(len(x[3]['destaques']) for x in out)} destaques" if PPL else ""))
