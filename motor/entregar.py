"""Entrega de um vídeo aprovado: render → envio pro Drive → conferência → versão registrada → limpeza → backup.

Uso: python motor/entregar.py projetos/<slug>
Regras (CLAUDE.md):
  - saída: editados/<nome-do-bruto>-<padrão>.mp4 ; se já existir (reedição), -v2, -v3... (nunca sobrescreve)
  - só limpa o Mac DEPOIS de conferir que o vídeo subiu inteiro (tamanho + MD5). Se falhar, nada é apagado.
  - guarda as decisões (< 1 MB) e uma cópia do motor + padrão usados (versao/<data>/), pra reabrir igual.
"""
import datetime, glob, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive, registro

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = drive.RAIZ_PROJETO
pj = os.path.abspath(sys.argv[1]); slug = os.path.basename(pj)
p = json.load(open(os.path.join(pj, "projeto.json"), encoding="utf-8"))
comp = os.path.join(pj, "composicao")

# 1. render
os.makedirs(os.path.join(pj, "cache"), exist_ok=True)
local = os.path.join(pj, "cache", "entrega.mp4")
subprocess.run(["npx", "--yes", "hyperframes@0.8.150", "render", "-q", "delivery", "-o", local], cwd=comp,
               check=True, capture_output=True)

# 2. envio + conferência (nunca sobrescreve um editado anterior)
base = f"{os.path.splitext(p['bruto'])[0]}-{p['padrao']}"
existentes = {f["nome"] for f in drive.listar("editados")}
nome, v = base + ".mp4", 2
while nome in existentes:
    nome = f"{base}-v{v}.mp4"; v += 1
if not drive.enviar(local, "editados/" + nome):
    sys.exit(f"❌ O envio de {nome} não conferiu. Nada foi apagado do Mac; o vídeo continua em {local}.")

# 3. versão usada (motor + padrão), pra reabrir exatamente igual
hoje = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
ver = os.path.join(pj, "versao", hoje)
shutil.copytree(AQUI, os.path.join(ver, "motor"), ignore=shutil.ignore_patterns("__pycache__"))
for f in ("padrao.json", "PLAYBOOK.md"):
    src = os.path.join(RAIZ, "padroes", p["padrao"], f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(ver, f))
p.setdefault("entregas", []).append({"data": hoje, "arquivo": "editados/" + nome, "versao": "versao/" + hoje})
json.dump(p, open(os.path.join(pj, "projeto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 4. limpeza: só arquivos temporários de edição (as decisões ficam)
def tamanho(c):
    return sum(os.path.getsize(os.path.join(d, a)) for d, _, aa in os.walk(c) for a in aa) if os.path.isdir(c) else (os.path.getsize(c) if os.path.exists(c) else 0)

alvos = [os.path.join(pj, "cache"), os.path.join(comp, "assets", "img"), os.path.join(pj, "storyboard", "q"),
         os.path.join(comp, "renders"), os.path.join(comp, "snapshots"), os.path.join(comp, ".thumbnails"),
         os.path.join(comp, ".waveform-cache")]
alvos += glob.glob(os.path.join(comp, "assets", "*.mp4")) + glob.glob(os.path.join(comp, "assets", "*.webm"))
liberado = sum(tamanho(a) for a in alvos)
for a in alvos:
    shutil.rmtree(a, ignore_errors=True) if os.path.isdir(a) else (os.remove(a) if os.path.exists(a) else None)

registro.etapa(slug, "entregue", saida="editados/" + nome, entregue_em=hoje)

# 5. backup do projeto
b = subprocess.run([sys.executable, "-I", os.path.join(AQUI, "backup.py")], capture_output=True, text=True)

print(f"✅ Entregue: {nome} está em editados/ no seu Drive (conferido).")
print(f"Liberei {liberado / 1e6:.0f} MB no seu Mac (só arquivos temporários de edição). "
      "O vídeo e tudo o que é preciso pra reeditar estão guardados.")
print(("Backup do projeto: " + b.stdout.strip()) if b.returncode == 0 else f"⚠️ Backup não concluído: {b.stderr.strip()[-300:]}")
