"""Backup do projeto (tudo que NÃO é vídeo) num .zip em _backup/ no Drive. Mantém os 5 mais recentes.

Vai no zip: motor, padrões, marcas, decisões de cada vídeo, registro, CLAUDE.md, LEIA-ME, comandos (.claude).
Fica fora: vídeos (já estão no Drive), arquivos temporários, ferramentas instaladas, config local.
Uso: python motor/backup.py
"""
import datetime, os, sys, tempfile, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive

RAIZ = drive.RAIZ_PROJETO
FORA_PASTAS = {".git", "tools", "node_modules", "cache", "renders", "snapshots", ".thumbnails", ".waveform-cache",
               ".hyperframes", "saida", "entrada", "__pycache__", "q", "folha", "config"}
FORA_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".wav", ".m4a", ".mp3", ".aac")


def gerar_zip(destino):
    n = 0
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for d, pastas, arqs in os.walk(RAIZ):
            pastas[:] = [p for p in pastas if p not in FORA_PASTAS and not (p == "img" and "composicao" in d)]
            for a in arqs:
                if a.lower().endswith(FORA_EXT) or a == ".DS_Store":
                    continue
                f = os.path.join(d, a)
                z.write(f, os.path.relpath(f, RAIZ)); n += 1
    return n


if __name__ == "__main__":
    nome = f"video-editor-{datetime.datetime.now():%Y-%m-%d-%H%M}.zip"
    tmp = os.path.join(tempfile.mkdtemp(), nome)
    n = gerar_zip(tmp)
    mb = os.path.getsize(tmp) / 1e6
    ok = drive.enviar(tmp, "_backup/" + nome)
    os.remove(tmp)
    if not ok:
        sys.exit("backup não conferiu no Drive")
    drive.remover_backups_antigos(5)
    print(f"backup _backup/{nome} ({n} arquivos, {mb:.1f} MB) conferido")
