"""Checagem ao abrir o projeto no Claude Code (hook SessionStart em .claude/settings.json).

Só biblioteca padrão do Python (roda antes do setup). Nunca falha a sessão: em qualquer erro, só informa.
Saída: JSON com hookSpecificOutput.additionalContext (contexto pro Claude, não aparece como mensagem).
"""
import json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def checar():
    faltando = []
    for nome, ok in (("ffmpeg", shutil.which("ffmpeg")), ("node/npx", shutil.which("npx")),
                     ("ambiente Python (~/.video-skill)", os.path.exists(os.path.expanduser("~/.video-skill/bin/python"))),
                     ("rclone", shutil.which("rclone") or os.path.exists(os.path.expanduser("~/.local/bin/rclone")))):
        if not ok:
            faltando.append(nome)
    import drive
    amb = drive.ambiente()
    marcas = [m for m in os.listdir(os.path.join(RAIZ, "marcas")) if os.path.exists(os.path.join(RAIZ, "marcas", m, "marca.json"))] \
        if os.path.isdir(os.path.join(RAIZ, "marcas")) else []
    if faltando or not amb or not amb.get("configurado"):
        return ("[video-editor] Setup INCOMPLETO" + (f" (falta: {', '.join(faltando)})" if faltando else "")
                + ". Ao responder a primeira mensagem, avise a usuária em uma frase e indique o comando /video-editor-configurar. "
                "Não edite vídeos antes do setup.")
    linhas = ["[video-editor] Setup completo. Drive: " + drive.base() + ". Marcas: " + (", ".join(marcas) or "nenhuma") + "."]
    try:
        import registro
        brutos, sumidos = registro.situacao()
        novos = [b["bruto"] for b in brutos if b["etapa"] == "novo"]
        andamento = [f"{b['bruto']} ({b['etapa']})" for b in brutos if b["etapa"] not in ("novo", "entregue")]
        linhas.append(f"Vídeos novos em brutos/: {len(novos)}" + (f" — {', '.join(novos[:5])}" if novos else "") + ".")
        if andamento:
            linhas.append("Em andamento: " + ", ".join(andamento[:5]) + ".")
        if sumidos:
            linhas.append("Registrados mas fora de brutos/: " + ", ".join(v["bruto"] for v in sumidos[:5]) + ".")
        linhas.append("Na primeira resposta, mencione em uma frase os vídeos novos/em andamento (se houver) "
                      "e os comandos /video-editor-videos e /video-editor-editar.")
    except Exception as e:
        linhas.append(f"Não foi possível consultar o Drive agora ({str(e)[:120]}). Se a usuária pedir, rodar /video-editor-videos.")
    return " ".join(linhas)


try:
    ctx = checar()
except Exception as e:
    ctx = f"[video-editor] Checagem de início falhou ({str(e)[:150]}). Seguir normalmente."
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))
