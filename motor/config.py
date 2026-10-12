"""Carrega a configuração de um projeto: projeto.json + padrão (padroes/<nome>/padrao.json) + marca (marcas/<nome>/marca.json).

Motor = como editar (igual pra todos). Padrão = o visual. Marca = o criador (logo, glossário, cor do cenário).
"""
import json, os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Projeto:
    def __init__(self, pasta):
        self.dir = os.path.abspath(pasta)
        self.p = json.load(open(self.path("projeto.json"), encoding="utf-8"))
        self.padrao_dir = os.path.join(RAIZ, "padroes", self.p["padrao"])
        self.marca_dir = os.path.join(RAIZ, "marcas", self.p["marca"])
        self.S = json.load(open(os.path.join(self.padrao_dir, "padrao.json"), encoding="utf-8"))
        self.M = json.load(open(os.path.join(self.marca_dir, "marca.json"), encoding="utf-8"))

    def path(self, *p):
        return os.path.join(self.dir, *p)

    def padrao(self, *p):
        return os.path.join(self.padrao_dir, *p)

    def marca(self, *p):
        return os.path.join(self.marca_dir, *p)

    @property
    def assets(self):
        return self.path("composicao", "assets")

    def edicao(self):
        return json.load(open(self.path("edicao.json"), encoding="utf-8"))

    def lut(self):
        """LUT de cor aprovada (PLAYBOOK 1.1): 'marca' = a da marca; caminho = outra; null = manter o original."""
        g = self.p.get("grading", "marca")
        if not g:
            return None
        return self.marca(self.M["lut"]) if g == "marca" else os.path.join(RAIZ, g)

    def fundo_mesclado(self):
        """Configuração do fundo mesclado: a do padrão, com ajustes por vídeo em edicao.json (se houver)."""
        cfg = dict(self.S["fundo_mesclado"])
        cfg.update(self.edicao().get("fundo_mesclado_ajuste", {}))
        return cfg

    def zoom(self):
        z = dict(self.S["zoom"])
        z.update({k: v for k, v in self.edicao().get("zoom", {}).items() if k != "trechos"})
        z["trechos"] = self.edicao().get("zoom", {}).get("trechos", [])
        return z
