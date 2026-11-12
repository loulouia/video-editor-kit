"""Atualiza o editor de vídeo a partir do GitHub, sem precisar do programa git.

Pra instalações feitas pelo zip (sem pasta .git). Baixa a versão nova pela web (curl, que todo Mac tem)
e troca só as partes que são da autora: motor/, padroes/<cada padrão>, .claude/ (comandos, hook, painel),
CLAUDE.md, LEIA-ME.md. Nunca toca nos dados da pessoa: marcas/, config/, projetos/, registro.json.

O que a pessoa mudou nessas partes é sobrescrito (decisão da autora), mas antes de trocar guarda uma cópia
em config/backups-atualizacao/ (as 3 mais recentes). Se algo falhar no meio, desfaz tudo.

Uso (de dentro da pasta do editor):
  python3 motor/atualizar.py checar     → JSON: {"disponivel", "local", "remoto", "mudancas"}
  python3 motor/atualizar.py aplicar    → baixa e instala a versão mais recente
  python3 motor/atualizar.py aplicar --zip <arquivo.zip>   → instala de um zip local (testes)

Só biblioteca padrão do Python.
"""
import json, os, re, shutil, subprocess, sys, zipfile
from datetime import datetime

REPO = "loulouia/video-editor-kit"
RAMO = "main"
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ARQ_VERSAO = os.path.join(RAIZ, "config", "versao.json")
PASTA_BACKUP = os.path.join(RAIZ, "config", "backups-atualizacao")
MANTER_BACKUPS = 3
TMP_NOVO = os.path.join(RAIZ, ".atualizacao-novo")
TMP_ANTIGO = os.path.join(RAIZ, ".atualizacao-antigo")

# Dados da pessoa: nunca tocados, mesmo que venham na versão nova.
PROTEGIDOS = {"marcas", "config", "projetos", "registro.json", "editados", "saida", ".git",
              ".claude/settings.local.json"}
# Pastas em que cada item é trocado separadamente (ex.: um padrão criado pela pessoa, que não existe
# na versão nova, continua lá). Fora delas, cada item é trocado inteiro (ex.: motor/).
DESCER = {"", ".claude", "padroes", ".claude/skills", ".claude/mods"}
IGNORAR = {".DS_Store", "__pycache__"}
# Sem estes, o zip baixado não é o editor: não instala.
OBRIGATORIOS = ("motor/inicio.py", "motor/atualizar.py", "CLAUDE.md", ".claude/settings.json")


class Erro(Exception):
    pass


def curl(url, saida=None, tempo=20, cabecalhos=()):
    cmd = ["curl", "-fsSL", "--max-time", str(tempo)]
    for h in cabecalhos:
        cmd += ["-H", h]
    if saida:
        cmd += ["-o", saida]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, timeout=tempo + 10)
    if r.returncode != 0:
        raise Erro(f"falha ao acessar {url} ({r.stderr.decode(errors='replace').strip()[:200]})")
    return r.stdout.decode(errors="replace")


def versao_local():
    try:
        with open(ARQ_VERSAO) as f:
            return json.load(f).get("commit") or None
    except Exception:
        return None


def versao_remota(tempo=8):
    sha = curl(f"https://api.github.com/repos/{REPO}/commits/{RAMO}", tempo=tempo,
               cabecalhos=("Accept: application/vnd.github.sha",)).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Erro("resposta inesperada do GitHub ao consultar a versão")
    return sha


def mudancas(local, remoto, tempo=8):
    """Títulos das mudanças entre a versão instalada e a nova (vazio se não der pra saber)."""
    if not local:
        return []
    try:
        dados = json.loads(curl(f"https://api.github.com/repos/{REPO}/compare/{local}...{remoto}", tempo=tempo))
        return [c["commit"]["message"].splitlines()[0] for c in dados.get("commits", [])]
    except Exception:
        return []


def checar(tempo=8):
    local = versao_local()
    remoto = versao_remota(tempo)
    disponivel = local != remoto
    return {"disponivel": disponivel, "local": local, "remoto": remoto,
            "mudancas": mudancas(local, remoto, tempo) if disponivel else []}


def unidades(base, rel=""):
    """Itens que a atualização troca, relativos à raiz (só os que vêm na versão nova)."""
    saida = []
    for nome in sorted(os.listdir(os.path.join(base, rel))):
        r = f"{rel}/{nome}" if rel else nome
        if nome in IGNORAR or r in PROTEGIDOS:
            continue
        if r in DESCER and os.path.isdir(os.path.join(base, r)):
            saida += unidades(base, r)
        else:
            saida.append(r)
    return saida


def extrair(arquivo_zip, destino):
    """Extrai o zip do GitHub (que tem uma pasta de topo) direto em `destino`, mantendo permissões."""
    destino_abs = os.path.abspath(destino)
    with zipfile.ZipFile(arquivo_zip) as z:
        nomes = [i.filename for i in z.infolist() if i.filename.strip("/")]
        topos = {n.split("/", 1)[0] for n in nomes}
        prefixo = (topos.pop() + "/") if len(topos) == 1 and all("/" in n for n in nomes) else ""
        for info in z.infolist():
            rel = info.filename[len(prefixo):] if info.filename.startswith(prefixo) else info.filename
            if not rel.strip("/"):
                continue
            alvo = os.path.abspath(os.path.join(destino_abs, rel))
            if not alvo.startswith(destino_abs + os.sep):
                raise Erro(f"caminho suspeito no zip: {info.filename}")
            if info.is_dir():
                os.makedirs(alvo, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with z.open(info) as src, open(alvo, "wb") as dst:
                shutil.copyfileobj(src, dst)
            modo = (info.external_attr >> 16) & 0o777
            if modo:
                os.chmod(alvo, modo)


def fazer_backup(itens):
    """Zip com o estado atual de tudo que vai ser trocado. Mantém os MANTER_BACKUPS mais recentes."""
    os.makedirs(PASTA_BACKUP, exist_ok=True)
    nome = os.path.join(PASTA_BACKUP, f"antes-da-atualizacao-{datetime.now():%Y-%m-%d-%H%M%S}.zip")
    with zipfile.ZipFile(nome, "w", zipfile.ZIP_DEFLATED) as z:
        for u in itens:
            p = os.path.join(RAIZ, u)
            if os.path.isfile(p):
                z.write(p, u)
            elif os.path.isdir(p):
                for pasta, subs, arqs in os.walk(p):
                    subs[:] = [s for s in subs if s not in IGNORAR]
                    for a in arqs:
                        if a in IGNORAR:
                            continue
                        cheio = os.path.join(pasta, a)
                        z.write(cheio, os.path.relpath(cheio, RAIZ))
    antigos = sorted(f for f in os.listdir(PASTA_BACKUP) if f.startswith("antes-da-atualizacao-"))
    for f in antigos[:-MANTER_BACKUPS]:
        os.remove(os.path.join(PASTA_BACKUP, f))
    return nome


def remover(p):
    if os.path.isdir(p) and not os.path.islink(p):
        shutil.rmtree(p)
    elif os.path.lexists(p):
        os.remove(p)


def aplicar(zip_local=None):
    if os.path.isdir(os.path.join(RAIZ, ".git")):
        raise Erro("esta pasta usa git (instalação da autora ou via git). Nela, atualizar é com git pull, "
                   "não com este script")
    if not (os.path.isdir(os.path.join(RAIZ, "motor")) and os.path.isfile(os.path.join(RAIZ, "CLAUDE.md"))):
        raise Erro(f"{RAIZ} não parece a pasta do editor de vídeo (falta motor/ ou CLAUDE.md)")
    if os.path.exists(TMP_ANTIGO):
        raise Erro(f"uma atualização anterior foi interrompida no meio ({TMP_ANTIGO} existe). "
                   "Não apaguei nada: peça ajuda à autora do editor antes de tentar de novo")
    remover(TMP_NOVO)

    try:
        os.makedirs(TMP_NOVO)
        if zip_local:
            arquivo, versao = os.path.abspath(zip_local), "zip-local"
        else:
            versao = versao_remota()
            arquivo = os.path.join(TMP_NOVO, "_versao.zip")
            curl(f"https://codeload.github.com/{REPO}/zip/{versao}", saida=arquivo, tempo=600)
        novo = os.path.join(TMP_NOVO, "editor")
        extrair(arquivo, novo)
        falta = [o for o in OBRIGATORIOS if not os.path.isfile(os.path.join(novo, o))]
        if falta:
            raise Erro("o arquivo baixado não é o editor de vídeo (falta " + ", ".join(falta) + "). Nada foi trocado")

        itens = unidades(novo)
        backup = fazer_backup(itens)

        feitos = []  # (item, onde a versão antiga ficou guardada ou None)
        try:
            for u in itens:
                destino = os.path.join(RAIZ, u)
                guardado = None
                if os.path.lexists(destino):
                    guardado = os.path.join(TMP_ANTIGO, u)
                    os.makedirs(os.path.dirname(guardado), exist_ok=True)
                    os.rename(destino, guardado)
                feitos.append((u, guardado))
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                os.rename(os.path.join(novo, u), destino)
        except BaseException:
            for u, guardado in reversed(feitos):  # desfaz: devolve tudo como estava
                destino = os.path.join(RAIZ, u)
                remover(destino)
                if guardado:
                    os.rename(guardado, destino)
            remover(TMP_ANTIGO)
            raise

        os.makedirs(os.path.dirname(ARQ_VERSAO), exist_ok=True)
        with open(ARQ_VERSAO, "w") as f:
            json.dump({"commit": versao, "instalado_em": datetime.now().isoformat(timespec="seconds")}, f, indent=2)
        remover(TMP_ANTIGO)
        return {"versao": versao, "itens": itens, "backup": backup}
    finally:
        remover(TMP_NOVO)


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    try:
        if cmd == "checar":
            print(json.dumps(checar(), ensure_ascii=False, indent=2))
        elif cmd == "aplicar":
            zip_local = args[args.index("--zip") + 1] if "--zip" in args else None
            antes = versao_local()
            r = aplicar(zip_local)
            if antes == r["versao"]:
                print("O editor já estava na versão mais recente (reinstalei a mesma versão).")
            print(f"Atualização instalada ({len(r['itens'])} itens trocados: motor, padrões, comandos).")
            print("Marcas, projetos, vídeos e a conexão com o Drive não foram alterados.")
            print(f"Cópia do que existia antes: {os.path.relpath(r['backup'], RAIZ)}")
        else:
            print(__doc__)
            sys.exit(2)
    except Erro as e:
        print(f"ERRO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
