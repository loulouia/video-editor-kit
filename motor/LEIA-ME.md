# Motor de edição

Scripts genéricos: leem `projetos/<slug>/projeto.json` (padrão, marca, aceleração, grading), o padrão (`padroes/<nome>/padrao.json`) e a marca (`marcas/<nome>/marca.json`). Rodar sempre com o Python do ambiente `~/.video-skill` e `-I`.

```
PY="$HOME/.video-skill/bin/python -I"
PJ=projetos/<slug>
B=<scratchpad>/bruto.mp4        # cópia local do bruto (evita travar com o iCloud)
```

| # | Etapa | Comando | Saída |
|---|---|---|---|
| 1 | Transcrever o bruto (com o glossário da marca) | `$PY motor/transcrever.py $PJ $B bruto` | `transcricao/bruto.words.json` |
| 2 | Propor cortes de pausa/respiração | `$PY motor/refinar_cortes.py $PJ $B` | `cortes.json` (+ início falso à mão) |
| 3 | **Validar cortes pela energia do áudio** | `$PY motor/energia.py $PJ $B` (`--perfil de ate`) | relatório OK/⚠️ |
| 4 | Gerar LUT de cor (só se a marca ainda não tiver) | `$PY motor/grading.py --bruto $B --ref ... --saida marcas/<m>/cor/x.cube --comparar x.jpg` | `.cube` + comparação |
| 5 | A-roll: cortes + aceleração + cor | `$PY motor/cortes.py $PJ $B` | `composicao/assets/aroll.mp4` |
| 6 | Conferir o A-roll | `$PY motor/transcrever.py $PJ $PJ/composicao/assets/aroll.mp4 aroll` | `transcricao/aroll.words.json` |
| 6b | **Storyboard (aprovação antes de montar)** | `$PY motor/storyboard.py $PJ` | `storyboard/storyboard.jpg` |
| 7 | Recorte da pessoa | `npx hyperframes remove-background $PJ/composicao/assets/aroll.mp4 -o $PJ/cache/subject.webm` | `cache/subject.webm` |
| 8 | Mapa do rosto (completo; o storyboard usa `--rapido`) | `$PY motor/rosto.py $PJ/composicao/assets/aroll.mp4 $PJ/cache/subject.webm $PJ/cache/rosto.json` | `cache/rosto.json` |
| 9 | Camadas (fundo mesclado, texto atrás) | `$PY motor/compor_camadas.py $PJ` | `composicao/assets/aroll_comp.mp4` |
| 10 | Composição (legendas, palavras-chave, cards, título, logo) | `$PY motor/gerar.py $PJ` | `composicao/index.html` |
| 11 | Validar e conferir | `npx hyperframes check` e `npx hyperframes snapshot --at ...` em `composicao/` | — |

O projeto HyperFrames (`composicao/`) é criado com `npx hyperframes init composicao --example blank --resolution portrait --non-interactive --skill general-video`. As inserções do vídeo vão pra `composicao/assets/img/`.

`config.py` carrega tudo; `Projeto(pasta)` expõe `S` (padrão), `M` (marca), `p` (projeto), `edicao()`, `lut()`, `fundo_mesclado()`, `zoom()`.
