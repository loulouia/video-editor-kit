"""Registro único dos vídeos (registro.json na raiz): o que é novo, o que está em andamento, o que foi entregue.

Um bruto é reconhecido pelo ID do arquivo no Drive (não muda se o usuário renomear); sem ID, por tamanho + data.
Só arquivos DIRETO em brutos/ são brutos. Nada no Drive é renomeado, movido ou apagado.

Uso:
  python motor/registro.py                          → tabela de status (consulta o Drive)
  python motor/registro.py --json                   → o mesmo, em JSON
  python motor/registro.py iniciar "<bruto>" <padrão> <marca>   → cria projetos/<slug>/ e registra (etapa "plano")
  python motor/registro.py etapa <slug> <etapa>     → plano | storyboard | montagem | preview | entregue
"""
import datetime, json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive

RAIZ = drive.RAIZ_PROJETO
ARQ = os.path.join(RAIZ, "registro.json")
VIDEO = (".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi")
SUSPEITO = re.compile(r"(?i)b[-_ ]?roll|broll|insert|insercao|inserção")
ICONE = {"novo": "🆕 novo", "plano": "⏳ plano", "storyboard": "⏳ storyboard", "montagem": "⏳ montagem",
         "preview": "⏳ preview", "entregue": "✅ entregue"}


def carregar():
    return json.load(open(ARQ, encoding="utf-8")) if os.path.exists(ARQ) else {"videos": []}


def salvar(r):
    json.dump(r, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def slugify(nome):
    base = os.path.splitext(nome)[0]
    s = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "video"


def achar(r, arq):
    for v in r["videos"]:
        if arq.get("id") and v.get("id") == arq["id"]:
            return v
    for v in r["videos"]:
        if v["bruto"] == arq["nome"] and v.get("tamanho") == arq["tamanho"]:
            return v
    for v in r["videos"]:
        if v.get("tamanho") == arq["tamanho"] and v.get("data") == arq["data"]:
            return v        # renomeado no Drive
    return None


def situacao():
    r = carregar()
    brutos = [a for a in drive.listar("brutos") if "/" not in a["nome"] and a["nome"].lower().endswith(VIDEO)]
    linhas = []
    for a in brutos:
        v = achar(r, a)
        if v and v["bruto"] != a["nome"]:
            v["renomeado_para"] = a["nome"]
        linhas.append({"bruto": a["nome"], "tamanho_mb": round(a["tamanho"] / 1e6, 1),
                       "etapa": v["etapa"] if v else "novo", "slug": v["slug"] if v else None,
                       "padrao": v.get("padrao") if v else None, "saida": v.get("saida") if v else None,
                       "suspeito_broll": bool(SUSPEITO.search(a["nome"]))})
    no_drive = {a["id"] for a in brutos if a.get("id")}
    sumidos = [v for v in r["videos"] if v.get("id") and v["id"] not in no_drive]
    return linhas, sumidos


def iniciar(nome, padrao, marca):
    r = carregar()
    arq = next((a for a in drive.listar("brutos") if a["nome"] == nome), None)
    if not arq:
        sys.exit(f"'{nome}' não está em brutos/ no Drive")
    v = achar(r, arq)
    if v:
        return v
    slug, n = slugify(nome), 2
    while any(x["slug"] == slug for x in r["videos"]) or os.path.exists(os.path.join(RAIZ, "projetos", slug)):
        slug = f"{slugify(nome)}-{n}"; n += 1
    pj = os.path.join(RAIZ, "projetos", slug)
    os.makedirs(os.path.join(pj, "transcricao"), exist_ok=True)
    json.dump({"titulo": os.path.splitext(nome)[0], "padrao": padrao, "marca": marca, "bruto": nome,
               "bruto_drive": "brutos/" + nome, "insercoes_drive": "insercoes/" + os.path.splitext(nome)[0],
               "aceleracao": None, "grading": None, "logo": None},
              open(os.path.join(pj, "projeto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    v = {"bruto": nome, "id": arq.get("id", ""), "tamanho": arq["tamanho"], "data": arq["data"], "slug": slug,
         "padrao": padrao, "marca": marca, "etapa": "plano", "inicio": datetime.date.today().isoformat()}
    r["videos"].append(v); salvar(r)
    return v


def etapa(slug, nova, **extra):
    r = carregar()
    v = next(x for x in r["videos"] if x["slug"] == slug)
    v["etapa"] = nova; v.update(extra); salvar(r)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "iniciar":
        print(json.dumps(iniciar(a[1], a[2], a[3]), ensure_ascii=False))
    elif a and a[0] == "etapa":
        etapa(a[1], a[2]); print("ok")
    else:
        linhas, sumidos = situacao()
        if "--json" in a:
            print(json.dumps({"brutos": linhas, "sumidos_do_drive": sumidos}, ensure_ascii=False, indent=1))
        else:
            if not linhas:
                print("Nenhum vídeo em brutos/ no Drive.")
            for l in linhas:
                extra = f" → {l['saida']}" if l["saida"] else ""
                aviso = "   ⚠️ nome parece de b-roll: confirmar" if l["suspeito_broll"] and l["etapa"] == "novo" else ""
                print(f"{ICONE.get(l['etapa'], l['etapa']):16} {l['bruto']} ({l['tamanho_mb']} MB){extra}{aviso}")
            for v in sumidos:
                print(f"⚠️  {v['bruto']} ({v['etapa']}) não está mais em brutos/ no Drive")
