---
name: video-editor-editar
description: Edita um vídeo bruto do Drive no editor de vídeo (video-editor) — pergunta padrão e cor, monta o plano, mostra o storyboard pra aprovação, monta e abre o preview. Também reabre um vídeo já entregue pra ajustes. Use quando a pessoa pedir pra editar, começar, continuar ou ajustar um vídeo.
argument-hint: "[nome do bruto]"
---

# Editar um vídeo

Bruto pedido: $ARGUMENTS (se vazio, rodar `motor/registro.py` e perguntar qual). Seguir o fluxo do `CLAUDE.md` (plano → storyboard → montagem → preview); comandos do motor em `motor/LEIA-ME.md`. Nunca pular uma aprovação.

## Escolha do modo de edição

Depois de definir o padrão e a marca, **sempre perguntar ao usuário** qual modo prefere, explicando de forma simples:

> **Como você quer editar?**
>
> 1. **Direto ao resultado** — Eu faço tudo sozinho (cortes, legendas, zoom, montagem) e te mostro o vídeo pronto pra você assistir e pedir ajustes. Mais rápido.
> 2. **Passo a passo** — Eu te mostro cada decisão antes de aplicar (onde cortar, o que escrever, como montar). Você aprova cada etapa. Mais controle.

- Se o usuário escolher **Direto ao resultado** → modo bypass (ver abaixo).
- Se o usuário escolher **Passo a passo** → fluxo normal com aprovações.
- Na dúvida ou sem resposta clara → usar **Direto ao resultado** como padrão.

## Vídeo novo — Fluxo normal (passo a passo)

1. **Padrão:** se `marca.json` tiver `padrao_padrao`, usar e avisar; senão **perguntar** (listar `padroes/`). **Marca:** se houver só uma, usar; se houver mais de uma, **perguntar qual** (listar `marcas/`), nunca escolher a primeira da lista.
2. `motor/registro.py iniciar "<bruto>" <padrão> <marca>` → cria `projetos/<slug>/`.
3. `motor/preparar.py projetos/<slug>` → baixa o bruto (cópia temporária) e as inserções de `insercoes/<nome-do-bruto>/`.
4. Conferir se é mesmo um bruto: tem fala? Se não tiver fala ou for muito curto → perguntar antes de seguir.
5. **Cor:** mostrar comparação (original × cor da marca × referência) e perguntar. Gravar em `projeto.json`.
6. Transcrever, propor cortes, **validar pela energia** (`energia.py`), escolher aceleração → `cortes.py` → A-roll.
7. **Plano** (tabela de inserções com fala exata, entra/sai, duração, tipo, origem; pergunta do gancho; recursos opcionais só se pedidos). Imagens que eu buscar: depois de escolhidas, **enviar pra `insercoes/<nome-do-bruto>/` no Drive** (`drive.py enviar`) e copiar pra `composicao/assets/img/`.
8. **Storyboard:** `motor/storyboard.py` → mandar `storyboard/storyboard.jpg`. Corrigir pelo número do quadro. `registro.py etapa <slug> storyboard`.
9. Aprovado → recorte (`remove-background`), `rosto.py`, `compor_camadas.py`, `gerar.py`, `hyperframes check` + snapshots → abrir o **preview** (HyperFrames, navegador do app). `registro.py etapa <slug> preview`.
10. Ajustes no preview até a aprovação. Pra entregar: `/video-editor-entregar`.

## Vídeo novo — Modo bypass (direto ao resultado)

Executa todas as etapas do fluxo normal **sem pedir confirmação**, usando as melhores decisões automáticas:

1. Padrão e marca: já definidos antes do bypass.
2. `registro.py iniciar` + `preparar.py` → baixa tudo.
3. Cor: usar a cor da marca (padrão). Se não tiver, manter original.
4. Transcrever, cortar, validar energia, aceleração → `cortes.py` → A-roll.
5. Plano: montar automaticamente seguindo as regras do PLAYBOOK do padrão. Inserções do gancho: usar o padrão do PLAYBOOK. Recursos opcionais: só os que o padrão liga por padrão.
6. Storyboard: gerar mas **não mostrar** (fica salvo pra consulta posterior).
7. Recorte, `rosto.py`, `compor_camadas.py`, `gerar.py`, snapshots → abrir o **preview**.
8. `registro.py etapa <slug> preview`.
9. Mostrar o preview e dizer: **"Pronto! Assista ao vídeo e me diga o que quer ajustar."**

**Tudo é executado corretamente no backend** — as mesmas etapas, os mesmos arquivos, a mesma qualidade. A diferença é só que o usuário não precisa aprovar cada passo.

## Vídeo já entregue (ajuste)

Perguntar: **igual à versão entregue** (padrão) ou **com o padrão atualizado**? → `motor/reabrir.py projetos/<slug> [--padrao-atual]` (~5–10 min) → abrir o preview. A nova entrega vira `-v2` em `editados/` (a anterior nunca é sobrescrita).

Também oferecer a escolha de modo (bypass ou passo a passo) antes de reabrir. No bypass, usar "igual à versão entregue" como padrão e ir direto ao preview.

## Disco

Antes de baixar, checar `df -h ~`. Se houver pouco espaço (< ~3 GB), avisar e sugerir entregar/limpar outros vídeos em andamento primeiro.
