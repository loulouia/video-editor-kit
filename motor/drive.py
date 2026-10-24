"""Transporte de vídeos entre o Drive e o Mac (rclone). Nunca renomeia, move ou apaga arquivos do usuário no Drive.

Configuração: config/ambiente.json → {"remote": "gdrive:", "raiz": "Edição de vídeos"}
  - em testes, "remote" pode ser uma pasta local (ex.: "/tmp/drive-teste/"), sem tocar no Drive.

Uso (CLI):
  python motor/drive.py status                       → rclone instalado? remote autorizado? estrutura existe?
  python motor/drive.py criar-estrutura              → cria as pastas que faltam (só depois do OK do usuário)
  python motor/drive.py listar brutos                → JSON com nome, tamanho, data, id
  python motor/drive.py baixar <caminho> <destino>   → copia do Drive pro Mac
  python motor/drive.py enviar <arquivo> <caminho>   → copia do Mac pro Drive e CONFERE (tamanho + MD5)
  python motor/drive.py copiar-biblioteca            → copia a biblioteca inicial (efeitos, músicas, transições)
                                                       da pasta compartilhada pra o Drive do cliente
"""
import hashlib, json, os, shutil, subprocess, sys

RAIZ_PROJETO = os.environ.get("VE_RAIZ") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AMBIENTE = os.path.join(RAIZ_PROJETO, "config", "ambiente.json")
PASTAS = ["brutos", "insercoes", "editados", "_padroes", "_marca", "_backup",
          "_audio/musicas", "_audio/efeitos", "_transicoes"]   # biblioteca compartilhada por todos os projetos e padrões


def rclone_bin():
    return shutil.which("rclone") or (os.path.expanduser("~/.local/bin/rclone") if os.path.exists(os.path.expanduser("~/.local/bin/rclone")) else None)


def ambiente():
    if not os.path.exists(AMBIENTE):
        return None
    return json.load(open(AMBIENTE, encoding="utf-8"))


def base():
    a = ambiente() or {}
    return a.get("remote", "gdrive:") + a.get("raiz", "Edição de vídeos")


def rc(*args, check=True, timeout=None):
    r = subprocess.run([rclone_bin(), *args], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip() or f"rclone {' '.join(args)} falhou")
    return r


def caminho(rel=""):
    return base() + ("/" + rel.strip("/") if rel else "")


def status():
    st = {"rclone": bool(rclone_bin()), "ambiente": bool(ambiente()), "autorizado": False, "pastas_faltando": PASTAS}
    if st["rclone"] and st["ambiente"]:
        remote = ambiente().get("remote", "gdrive:")
        if remote.endswith(":") and remote.rstrip(":") not in [x.rstrip(":") for x in rc("listremotes", check=False).stdout.split()]:
            return st
        r = rc("lsjson", "--dirs-only", "-R", "--max-depth", "2", caminho(), check=False, timeout=60)
        st["autorizado"] = r.returncode == 0 or "directory not found" in r.stderr
        if r.returncode == 0:
            existentes = {d["Path"] for d in json.loads(r.stdout or "[]")}
            st["pastas_faltando"] = [p for p in PASTAS if p not in existentes]
    return st


def criar_estrutura():
    for p in PASTAS:
        rc("mkdir", caminho(p))
    return status()


def listar(rel, recursivo=False):
    args = ["lsjson", "--files-only", "--hash", caminho(rel)]
    if recursivo:
        args.insert(1, "-R")
    r = rc(*args, check=False, timeout=120)
    if r.returncode and "directory not found" in r.stderr:
        return []
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    return [{"nome": f["Path"], "tamanho": f["Size"], "data": f["ModTime"], "id": f.get("ID", ""),
             "md5": (f.get("Hashes") or {}).get("md5", "")} for f in json.loads(r.stdout or "[]")]


def md5(arquivo):
    h = hashlib.md5()
    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar(rel, destino):
    os.makedirs(os.path.dirname(os.path.abspath(destino)) or ".", exist_ok=True)
    rc("copyto", caminho(rel), destino)
    return destino


def baixar_pasta(rel, destino):
    os.makedirs(destino, exist_ok=True)
    r = rc("copy", caminho(rel), destino, check=False)
    if r.returncode and "directory not found" not in r.stderr:
        raise RuntimeError(r.stderr.strip())
    return sorted(os.listdir(destino))


def enviar(arquivo, rel):
    """Envia e confere. Só retorna True se o arquivo no Drive tem o mesmo tamanho e o mesmo MD5 do local."""
    rc("copyto", arquivo, caminho(rel))
    pasta, nome = os.path.split(rel.strip("/"))
    remoto = next((f for f in listar(pasta) if f["nome"] == nome), None)
    if not remoto or remoto["tamanho"] != os.path.getsize(arquivo):
        return False
    return not remoto["md5"] or remoto["md5"] == md5(arquivo)


def copiar_biblioteca():
    """Copia a biblioteca inicial (efeitos, músicas, transições) de uma pasta compartilhada no Drive para o Drive do cliente.
    Usa --drive-root-folder-id pra acessar a pasta compartilhada pelo ID, independente de ela estar em 'Meu Drive' ou 'Compartilhados comigo'."""
    a = ambiente()
    if not a or "biblioteca" not in a:
        return {"ok": False, "erro": "sem configuração de biblioteca em ambiente.json"}
    bib = a["biblioteca"]
    pasta_id = bib.get("pasta_id")
    destinos = bib.get("destinos", {})
    if not pasta_id or not destinos:
        return {"ok": False, "erro": "biblioteca mal configurada"}

    remote = a.get("remote", "gdrive:").rstrip(":")
    origem_remote = f"{remote},root_folder_id={pasta_id}:"
    resultado = {}
    total_arquivos = 0
    for sub, destino_rel in destinos.items():
        origem = f"{origem_remote}{sub}"
        destino = caminho(destino_rel)
        try:
            r = rc("copy", origem, destino, check=False, timeout=900)
        except subprocess.TimeoutExpired:
            resultado[sub] = {"ok": False, "erro": "timeout — arquivos muito grandes; tente de novo"}
            continue
        if r.returncode and "directory not found" not in r.stderr:
            resultado[sub] = {"ok": False, "erro": r.stderr.strip()}
        else:
            arquivos = listar(destino_rel)
            resultado[sub] = {"ok": True, "arquivos": len(arquivos)}
            total_arquivos += len(arquivos)
    resultado["total"] = total_arquivos
    return resultado


def remover_backups_antigos(manter=5):
    """Único caso em que algo é apagado no Drive: backups antigos que o próprio motor criou em _backup/."""
    zips = sorted(f["nome"] for f in listar("_backup") if f["nome"].startswith("video-editor-") and f["nome"].endswith(".zip"))
    for z in zips[:-manter]:
        rc("deletefile", caminho("_backup/" + z))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status(), ensure_ascii=False))
    elif cmd == "criar-estrutura":
        print(json.dumps(criar_estrutura(), ensure_ascii=False))
    elif cmd == "listar":
        print(json.dumps(listar(sys.argv[2], "-R" in sys.argv), ensure_ascii=False, indent=1))
    elif cmd == "baixar":
        print(baixar(sys.argv[2], sys.argv[3]))
    elif cmd == "enviar":
        ok = enviar(sys.argv[2], sys.argv[3]); print("conferido" if ok else "FALHOU"); sys.exit(0 if ok else 1)
    elif cmd == "copiar-biblioteca":
        print(json.dumps(copiar_biblioteca(), ensure_ascii=False, indent=1))
    else:
        sys.exit(__doc__)
