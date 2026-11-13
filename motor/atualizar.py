"""Atualiza o editor de vídeo a partir do GitHub, sem precisar do programa git.

Pra instalações feitas pelo zip (sem pasta .git). Baixa a versão nova pela web (curl, que todo Mac tem)
e troca só as partes que são da autora: motor/, padroes/<cada padrão>, .claude/ (comandos, hook, painel),
CLAUDE.md, LEIA-ME.md. Nunca toca nos dados da pessoa: marcas/, config/, projetos/, registro.json.

O que a pessoa mudou nessas partes é sobrescrito (decisão da autora), mas antes de trocar guarda uma cópia
em config/backups-atualizacao/ (as 3 mais recentes). Se algo falhar no meio, desfaz tudo.

Uso (de dentro da pasta do editor):
  python3 motor/atualizar.py checar     → JSON: {"disponivel", "local", "remoto", "mudancas"}
  python3 motor/atualizar.py aplicar    → baixa e instala a versão mais recente
  python3 motor/atualizar.py desfazer   → volta pra versão de antes da última atualização (usa a cópia guardada)
  python3 motor/atualizar.py aplicar --zip <arquivo.zip>   → instala de um zip local (testes)

Se `python3` não funcionar, usar `~/.video-skill/bin/python` (criado no setup) no lugar.

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


SEM_INTERNET = ("não consegui baixar do GitHub (sem internet ou o site não respondeu). Nada foi trocado. "
                "Confira a conexão e tente de novo daqui a alguns minutos")


def curl(url, saida=None, tempo=20, cabecalhos=(), tentativas=3):
    cmd = ["curl", "-fsSL", "--max-time", str(tempo), "--retry", str(tentativas - 1), "--retry-delay", "3"]
    for h in cabecalhos:
        cmd += ["-H", h]
    if saida:
        cmd += ["-o", saida]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=(tempo + 5) * tentativas + 10)
    except (OSError, subprocess.TimeoutExpired):
        raise Erro(SEM_INTERNET)
    if r.returncode != 0:
        raise Erro(SEM_INTERNET + f" [detalhe técnico: {r.stderr.decode(errors='replace').strip()[:150]}]")
    return r.stdout.decode(errors="replace")


def versao_local():
    try:
        with open(ARQ_VERSAO) as f:
            return json.load(f).get("commit") or None
    except Exception:
        return None


def versao_remota(tempo=8):
    sha = curl(f"https://api.github.com/repos/{REPO}/commits/{RAMO}", tempo=tempo, tentativas=1,
               cabecalhos=("Accept: application/vnd.github.sha",)).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise Erro("resposta inesperada do GitHub ao consultar a versão")
    return sha


def mudancas(local, remoto, tempo=8):
    """Títulos das mudanças entre a versão instalada e a nova (vazio se não der pra saber)."""
    if not local:
        return []
    try:
        dados = json.loads(curl(f"https://api.github.com/repos/{REPO}/compare/{local}...{remoto}", tempo=tempo,
                                tentativas=1))
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


MANIFESTO = "_atualizacao.json"  # dentro do zip de cópia: itens trocados e versão anterior (usado pelo desfazer)


def fazer_backup(itens):
    """Zip com o estado atual de tudo que vai ser trocado. Mantém os MANTER_BACKUPS mais recentes."""
    os.makedirs(PASTA_BACKUP, exist_ok=True)
    nome = os.path.join(PASTA_BACKUP, f"antes-da-atualizacao-{datetime.now():%Y-%m-%d-%H%M%S}.zip")
    with zipfile.ZipFile(nome, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(MANIFESTO, json.dumps({"itens": itens, "versao_anterior": versao_local()}, indent=2))
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


def pasta_da_autora(raiz=RAIZ):
    """A pasta de trabalho da autora: tem o arquivo-marcador `.autora` (ignorado pelo git, nunca vai pros clientes) ou o
    repositório git com a marca dela. Só ela atualiza com git; todo cliente atualiza por aqui, mesmo que tenha instalado
    com git (git no Mac exige as ferramentas da Apple)."""
    return os.path.exists(os.path.join(raiz, ".autora")) or \
        (os.path.isdir(os.path.join(raiz, ".git")) and os.path.isdir(os.path.join(raiz, "marcas", "amanda")))


def checar_pasta():
    if pasta_da_autora():
        raise Erro("esta é a pasta de trabalho da autora (git). Nela, atualizar é com git pull, não com este script")
    if not (os.path.isdir(os.path.join(RAIZ, "motor")) and os.path.isfile(os.path.join(RAIZ, "CLAUDE.md"))):
        raise Erro(f"{RAIZ} não parece a pasta do editor de vídeo (falta motor/ ou CLAUDE.md). "
                   "Rode de dentro da pasta do editor (a que tem as pastas motor e padroes)")


def trocar(origem, itens, guarda):
    """Troca cada item da raiz pelo de `origem` (item ausente em `origem` é só retirado).
    As versões atuais vão pra `guarda` até o fim; se qualquer passo falhar, devolve tudo como estava."""
    feitos = []  # (item, onde a versão atual ficou guardada ou None)
    try:
        for u in itens:
            destino = os.path.join(RAIZ, u)
            guardado = None
            if os.path.lexists(destino):
                guardado = os.path.join(guarda, u)
                os.makedirs(os.path.dirname(guardado), exist_ok=True)
                os.rename(destino, guardado)
            feitos.append((u, guardado))
            vindo = os.path.join(origem, u)
            if os.path.lexists(vindo):
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                os.rename(vindo, destino)
    except BaseException:
        for u, guardado in reversed(feitos):
            destino = os.path.join(RAIZ, u)
            remover(destino)
            if guardado:
                os.rename(guardado, destino)
        remover(guarda)
        raise
    remover(guarda)


def gravar_versao(versao):
    os.makedirs(os.path.dirname(ARQ_VERSAO), exist_ok=True)
    if versao is None:
        remover(ARQ_VERSAO)
        return
    with open(ARQ_VERSAO, "w") as f:
        json.dump({"commit": versao, "instalado_em": datetime.now().isoformat(timespec="seconds")}, f, indent=2)


def aplicar(zip_local=None):
    checar_pasta()
    if os.path.exists(TMP_ANTIGO):
        raise Erro("uma atualização anterior foi interrompida no meio (ex.: o Mac desligou). Nada foi apagado. "
                   "Rode primeiro: python3 motor/atualizar.py desfazer — e depois tente atualizar de novo")
    remover(TMP_NOVO)

    try:
        os.makedirs(TMP_NOVO)
        if zip_local:
            arquivo, versao = os.path.abspath(zip_local), "zip-local"
        else:
            # Um download só: o zip do GitHub traz o código da versão (commit) no comentário do arquivo.
            arquivo = os.path.join(TMP_NOVO, "_versao.zip")
            curl(f"https://codeload.github.com/{REPO}/zip/refs/heads/{RAMO}", saida=arquivo, tempo=600)
            try:
                with zipfile.ZipFile(arquivo) as z:
                    versao = z.comment.decode(errors="replace").strip()
            except zipfile.BadZipFile:
                raise Erro("o download veio incompleto ou corrompido. Nada foi trocado. Tente de novo")
            if not re.fullmatch(r"[0-9a-f]{40}", versao):
                versao = "desconhecida"
        novo = os.path.join(TMP_NOVO, "editor")
        extrair(arquivo, novo)
        falta = [o for o in OBRIGATORIOS if not os.path.isfile(os.path.join(novo, o))]
        if falta:
            raise Erro("o arquivo baixado não é o editor de vídeo (falta " + ", ".join(falta) + "). Nada foi trocado")

        itens = unidades(novo)
        backup = fazer_backup(itens)
        trocar(novo, itens, TMP_ANTIGO)
        gravar_versao(versao)
        return {"versao": versao, "itens": itens, "backup": backup}
    finally:
        remover(TMP_NOVO)


def desfazer():
    """Volta pra versão de antes da última atualização, a partir da cópia em config/backups-atualizacao/.
    Também resolve uma atualização interrompida no meio (a cópia é feita antes de trocar qualquer coisa)."""
    checar_pasta()
    copias = sorted(f for f in os.listdir(PASTA_BACKUP) if f.startswith("antes-da-atualizacao-")) \
        if os.path.isdir(PASTA_BACKUP) else []
    if not copias:
        raise Erro("não há cópia guardada de antes de uma atualização. Nada foi alterado")
    copia = os.path.join(PASTA_BACKUP, copias[-1])
    with zipfile.ZipFile(copia) as z:
        manifesto = json.loads(z.read(MANIFESTO))
    restaurado = os.path.join(TMP_NOVO, "restaurar")
    interrompida = os.path.exists(TMP_ANTIGO)
    remover(TMP_NOVO)
    try:
        extrair(copia, restaurado)
        trocar(restaurado, manifesto["itens"], TMP_ANTIGO + "-desfazer")
        gravar_versao(manifesto.get("versao_anterior"))
        if interrompida:
            remover(TMP_ANTIGO)  # sobra da atualização interrompida; o conteúdo dela estava na cópia
        return {"copia": copia, "itens": manifesto["itens"], "interrompida": interrompida}
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
        elif cmd == "desfazer":
            r = desfazer()
            print("Pronto: o editor voltou pra versão de antes da última atualização"
                  + (" (a atualização interrompida foi desfeita)" if r["interrompida"] else "") + ".")
            print("Marcas, projetos, vídeos e a conexão com o Drive não foram alterados.")
        else:
            print(__doc__)
            sys.exit(2)
    except Erro as e:
        print(f"ERRO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO inesperado: {e}. O que já tinha sido trocado foi desfeito; marcas, projetos e Drive não "
              "foram tocados. Mande esta mensagem pra autora do editor.")
        sys.exit(1)


if __name__ == "__main__":
    main()
