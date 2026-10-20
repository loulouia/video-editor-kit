---
name: video-editor-editar
description: Edita um vídeo bruto do Drive no editor de vídeo (video-editor) — pergunta padrão e cor, monta o plano, mostra o storyboard pra aprovação, monta e abre o preview. Também reabre um vídeo já entregue pra ajustes. Use quando a pessoa pedir pra editar, começar, continuar ou ajustar um vídeo.
argument-hint: "[nome do bruto]"
---

# Editar um vídeo

Bruto pedido: $ARGUMENTS (se vazio, rodar `motor/registro.py` e perguntar qual). Seguir o fluxo do `CLAUDE.md` (plano → storyboard → montagem → preview); comandos do motor em `motor/LEIA-ME.md`. Nunca pular uma aprovação.

## Vídeo novo

1. **Padrão:** se `marca.json` tiver `padrao_padrao`, usar e avisar; senão **perguntar** (listar `padroes/`). **Marca:** se houver só uma, usar.
2. `motor/registro.py iniciar "<bruto>" <padrão> <marca>` → cria `projetos/<slug>/`.
3. `motor/preparar.py projetos/<slug>` → baixa o bruto (cópia temporária) e as inserções de `insercoes/<nome-do-bruto>/`.
4. Conferir se é mesmo um bruto: tem fala? Se não tiver fala ou for muito curto → perguntar antes de seguir.
5. **Cor:** mostrar comparação (original × cor da marca × referência) e perguntar. Gravar em `projeto.json`.
6. Transcrever, propor cortes, **validar pela energia** (`energia.py`), escolher aceleração → `cortes.py` → A-roll.
7. **Plano** (tabela de inserções com fala exata, entra/sai, duração, tipo, origem; pergunta do gancho; recursos opcionais só se pedidos). Imagens que eu buscar: depois de escolhidas, **enviar pra `insercoes/<nome-do-bruto>/` no Drive** (`drive.py enviar`) e copiar pra `composicao/assets/img/`.
8. **Storyboard:** `motor/storyboard.py` → mandar `storyboard/storyboard.jpg`. Corrigir pelo número do quadro. `registro.py etapa <slug> storyboard`.
9. Aprovado → recorte (`remove-background`), `rosto.py`, `compor_camadas.py`, `gerar.py`, `hyperframes check` + snapshots → abrir o **preview** (HyperFrames, navegador do app). `registro.py etapa <slug> preview`.
10. Ajustes no preview até a aprovação. Pra entregar: `/video-editor-entregar`.

## Vídeo já entregue (ajuste)

Perguntar: **igual à versão entregue** (padrão) ou **com o padrão atualizado**? → `motor/reabrir.py projetos/<slug> [--padrao-atual]` (~5–10 min) → abrir o preview. A nova entrega vira `-v2` em `editados/` (a anterior nunca é sobrescrita).

## Disco

Antes de baixar, checar `df -h ~`. Se houver pouco espaço (< ~3 GB), avisar e sugerir entregar/limpar outros vídeos em andamento primeiro.
