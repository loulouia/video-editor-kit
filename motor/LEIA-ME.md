# Motor de edição

Scripts genéricos: leem `projetos/<slug>/projeto.json` (padrão, marca, aceleração, grading), o padrão (`padroes/<nome>/padrao.json`) e a marca (`marcas/<nome>/marca.json`). Rodar sempre com o Python do ambiente `~/.video-skill` e `-I`.

```
PY="$HOME/.video-skill/bin/python -I"
PJ=projetos/<slug>
B=$PJ/cache/bruto.<ext>        # baixado do Drive por preparar.py
```

**Drive e registro** (`drive.py` usa `config/ambiente.json`; em teste, `"remote"` pode ser uma pasta local):

| Comando | Faz |
|---|---|
| `$PY motor/drive.py status` / `criar-estrutura` | confere / cria as pastas no Drive (criar só com OK) |
| `$PY motor/registro.py` | status dos brutos no Drive (novo / etapa / entregue) |
| `$PY motor/registro.py iniciar "<bruto>" <padrão> <marca>` | cria `projetos/<slug>/` e registra |
| `$PY motor/registro.py etapa <slug> <etapa>` | plano · storyboard · montagem · preview · entregue |
| `$PY motor/preparar.py $PJ` | baixa bruto (cache/) e inserções (composicao/assets/img/) |
| `$PY motor/entregar.py $PJ` | render → envio → conferência MD5 → versão → limpeza → backup |
| `$PY motor/reabrir.py $PJ [--padrao-atual]` | remonta um vídeo entregue a partir das decisões |
| `$PY motor/backup.py` | zip do projeto (sem vídeos) em `_backup/` (5 mais recentes) |
| `python3 motor/inicio.py` | checagem do início de sessão (hook) |

**Edição:**

| # | Etapa | Comando | Saída |
|---|---|---|---|
| 1 | Transcrever o bruto (com o glossário da marca) | `$PY motor/transcrever.py $PJ $B bruto` | `transcricao/bruto.words.json` |
| 2 | Propor cortes de pausa/respiração | `$PY motor/refinar_cortes.py $PJ $B` | `cortes.json` (+ início falso à mão) |
| 3 | **Validar cortes pela energia do áudio** | `$PY motor/energia.py $PJ $B` (`--perfil de ate`; `--sugerir --gravar` propõe cortes nas pausas reais) | relatório OK/⚠️ |
| 4 | Gerar LUT de cor (só se a marca ainda não tiver) | `$PY motor/grading.py --bruto $B --ref ... --saida marcas/<m>/cor/x.cube --comparar x.jpg` | `.cube` + comparação |
| 5 | A-roll: cortes + aceleração + cor | `$PY motor/cortes.py $PJ $B` | `composicao/assets/aroll.mp4` |
| 6 | Conferir o A-roll | `$PY motor/transcrever.py $PJ $PJ/composicao/assets/aroll.mp4 aroll` | `transcricao/aroll.words.json` |
| 6b | **Storyboard (aprovação antes de montar)** | `$PY motor/storyboard.py $PJ` | `storyboard/storyboard.jpg` |
| 7 | Recorte da pessoa | `npx hyperframes remove-background $PJ/composicao/assets/aroll.mp4 -o $PJ/cache/subject.webm` | `cache/subject.webm` |
| 8 | Mapa do rosto (completo; o storyboard usa `--rapido`) | `$PY motor/rosto.py $PJ/composicao/assets/aroll.mp4 $PJ/cache/subject.webm $PJ/cache/rosto.json` | `cache/rosto.json` |
| 9 | Camadas (fundo mesclado, texto atrás) | `$PY motor/compor_camadas.py $PJ` | `composicao/assets/aroll_comp.mp4` |
| 10 | Composição (legendas, palavras-chave, cards, título, logo) | `$PY motor/gerar.py $PJ` | `composicao/index.html` |
| 11 | Validar e conferir | `npx hyperframes check` e `npx hyperframes snapshot --at ...` em `composicao/` | — |

O projeto HyperFrames (`composicao/`) é criado com `npx hyperframes init composicao --example blank --resolution portrait --non-interactive --skill general-video`. As inserções do vídeo vêm do Drive (`insercoes/<nome-do-bruto>/`) pra `composicao/assets/img/`. Legendas: `motor/legendas.py $PJ --gravar` (limites do padrão).

`config.py` carrega tudo; `Projeto(pasta)` expõe `S` (padrão), `M` (marca), `p` (projeto), `edicao()`, `lut()`, `fundo_mesclado()`, `zoom()`.
