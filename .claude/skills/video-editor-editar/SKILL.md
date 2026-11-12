---
name: video-editor-editar
description: Edita um vídeo bruto do Drive no editor de vídeo (video-editor) — pergunta padrão e cor, monta o plano, mostra o storyboard pra aprovação, monta e abre o preview. Também reabre um vídeo já entregue pra ajustes. Use quando a pessoa pedir pra editar, começar, continuar ou ajustar um vídeo.
argument-hint: "[nome do bruto]"
---

# Editar um vídeo

Bruto pedido: $ARGUMENTS (se vazio, rodar `motor/registro.py` e perguntar qual). Seguir o fluxo do `CLAUDE.md` (plano → storyboard → montagem → preview); comandos do motor em `motor/LEIA-ME.md`. No **passo a passo**, nunca pular uma aprovação; no **direto ao resultado**, as aprovações viram decisões automáticas (abaixo) e a pessoa só aprova no preview.

## Escolha do modo de edição

Depois de definir o padrão e a marca, **sempre perguntar ao usuário** qual modo prefere, explicando de forma simples:

> **Como você quer editar?**
>
> 1. **Direto ao resultado** — Eu faço tudo sozinho (cortes, legendas, zoom, montagem) e te mostro o vídeo pronto pra você assistir e pedir ajustes. Mais rápido.
> 2. **Passo a passo** — Eu te mostro cada decisão antes de aplicar (onde cortar, o que escrever, como montar). Você aprova cada etapa. Mais controle.

- Se o usuário escolher **Direto ao resultado** → modo bypass (ver abaixo).
- Se o usuário escolher **Passo a passo** → fluxo normal com aprovações.
- Na dúvida ou sem resposta clara → usar **Direto ao resultado** como padrão.

## Opções do padrão (aceleração, glow)

Alguns padrões deixam opções para o usuário escolher em cada vídeo (`padrao.json` → `"recursos"` com valor `"opcional"`):

- **Aceleração** (`"aceleracao": "opcional"`, ex.: `basico`): o padrão é **não acelerar** (`aceleracao.padrao`, 1,0×). No passo a passo, perguntar junto com a cor: "Quer acelerar a fala? (sem aceleração / acelerar um pouco)". Se sim, escolher o fator em `aceleracao.opcional` (mín.–máx.) que mais aproxima `alvo_palavras_s`. Gravar em `projeto.json` → `"aceleracao"`.
- **Glow na legenda** (`"glow": "opcional"`): perguntar "Quer um leve brilho branco nas legendas?". Se sim, `projeto.json` → `"glow": true` (muda só o `gerar.py`).
- No **direto ao resultado**: não acelera e não usa glow. O usuário pode pedir no preview.

Padrões sem essas opções em `"recursos"` seguem a regra do PLAYBOOK (ex.: `amanda` acelera 1,10–1,15×).

## Cortes de pausas e respiros (padrões com `cortes.tom_min`, ex.: `basico`)

No lugar de `refinar_cortes.py` + `energia.py`: `motor/cortar_pausas.py projetos/<slug> <bruto>` corta toda pausa **e respiro** com 0,2 s ou mais (detector de fala pelo tom das cordas vocais, `motor/voz.py`; respiro é chiado sem tom). Depois de `cortes.py`, **conferir**: `transcrever.py ... aroll_conferencia` e comparar a lista de palavras com `bruto.words.json` (nenhuma palavra pode sumir; diferença de grafia/vogal é variação do Whisper, mas palavra faltando ou fim de palavra comido → transcrever o trecho isolado com e sem o corte e, se mudar, marcar o trecho em `projeto.json` → `cortes_config.manter`).

## Rosto e montagem (padrões com `legenda.palavra_por_palavra`, ex.: `basico`)

- **Recorte completo antes de montar**: `remove-background` + `rosto.py` com o recorte (o `--rapido` é só pro storyboard; em selfie de perto ele erra o queixo e a legenda pode cobrir a boca).
- **Zoom**: alternar aberto/fechado a cada corte (pausa ou respiro), em `edicao.json` → `zoom.trechos` (fronteiras dos trechos de `timeline.json` → `keep`).
- O `gerar.py` aplica sozinho a área segura do Instagram, divide blocos que não cabem abaixo do queixo e transforma em tela cheia o card que não cabe; ler os avisos (ℹ️/⚠️) e conferir nos snapshots os trechos avisados.
- Render com pouco disco: se `hyperframes render` falhar por espaço, usar `--workers 1` (não grava os quadros no disco).

## Legendas com destaques (padrões com `legenda.palavras_por_linha`, ex.: `basico`)

Antes, depois de transcrever o A-roll, rodar `motor/sincronizar.py projetos/<slug>`: o Whisper marca o começo das palavras adiantado (~0,13 s) e, palavra por palavra, a legenda apareceria antes da fala. `motor/legendas.py projetos/<slug>` propõe as linhas e as palavras de destaque. Antes de gravar (`--gravar`), **revisar**: trocar destaques fracos pela palavra que carrega o sentido do trecho (número, nome, conceito, conclusão), manter pelo menos um a cada 4 s, e corrigir quebras estranhas (pedaço solto, frase cortada no meio de expressão), editando `linhas`/`destaques`/`sozinha` no `edicao.json`. No passo a passo, mostrar a lista no plano. O `gerar.py` avisa se ficar mais de 4 s sem destaque.

## Vídeo novo — Fluxo normal (passo a passo)

1. **Padrão:** se `marca.json` tiver `padrao_padrao`, usar e avisar; senão **perguntar** (listar `padroes/`). **Marca:** se houver só uma, usar; se houver mais de uma, **perguntar qual** (listar `marcas/`), nunca escolher a primeira da lista.
2. `motor/registro.py iniciar "<bruto>" <padrão> <marca>` → cria `projetos/<slug>/`.
3. `motor/preparar.py projetos/<slug>` → baixa o bruto (cópia temporária) e as inserções de `insercoes/<nome-do-bruto>/`.
4. Conferir se é mesmo um bruto: tem fala? Se não tiver fala ou for muito curto → perguntar antes de seguir.
5. **Cor:** mostrar comparação (original × cor da marca × referência) e perguntar. Gravar em `projeto.json`. Se o padrão tiver opções (aceleração, glow), perguntar aqui também (ver "Opções do padrão").
6. Transcrever, propor cortes, **validar pela energia** (`energia.py`), escolher aceleração → `cortes.py` → A-roll.
7. **Plano** (tabela de inserções com fala exata, entra/sai, duração, tipo, origem; pergunta do gancho; recursos opcionais só se pedidos). Imagens que eu buscar: depois de escolhidas, **enviar pra `insercoes/<nome-do-bruto>/` no Drive** (`drive.py enviar`) e copiar pra `composicao/assets/img/`.
8. **Storyboard:** `motor/storyboard.py` → mandar `storyboard/storyboard.jpg`. Corrigir pelo número do quadro. `registro.py etapa <slug> storyboard`.
9. Aprovado → recorte (`remove-background`), `rosto.py`, `compor_camadas.py`, `gerar.py`, `hyperframes check` + snapshots → abrir o **preview** (HyperFrames, navegador do app). `registro.py etapa <slug> preview`.
10. Ajustes no preview até a aprovação. Pra entregar: `/video-editor-entregar`.

## Vídeo novo — Modo bypass (direto ao resultado)

Executa todas as etapas do fluxo normal **sem pedir confirmação**, usando as melhores decisões automáticas:

1. Padrão e marca: já definidos antes do bypass.
2. `registro.py iniciar` + `preparar.py` → baixa tudo.
3. Cor: rodar `motor/medir_cor.py <bruto>`. **Lavado** → `padroes/amanda/cor/lavado.cube` (`grading` = esse caminho); **normal** → cor da marca; marca sem cor → original. Nunca aplicar a cor da marca num bruto lavado (deixa ainda mais apagado).
4. Transcrever, cortar, validar energia, aceleração (padrão com aceleração opcional → sem aceleração) → `cortes.py` → A-roll.
5. Plano: montar automaticamente seguindo as regras do PLAYBOOK do padrão. Gancho: só o título de abertura (sem inserção). Inserções: as imagens de `insercoes/<nome-do-bruto>/` entram como card na base, no trecho da fala a que se referem (ou no tempo do prefixo do nome, ex. `0m12-`). Recursos opcionais: só os que o padrão liga por padrão.
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
