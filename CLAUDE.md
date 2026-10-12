# Regras de trabalho — editor de vídeo

Pipeline de edição de vídeos curtos (Reels/TikTok, 1080×1920) feito em código. Visão de uso: `LEIA-ME.md`. Comandos do pipeline: `motor/LEIA-ME.md`.

## Estrutura: motor, padrões, marcas, projetos

| Pasta | O que é | Muda entre… |
|---|---|---|
| `motor/` | **Como editar.** Scripts genéricos (cortes, cor, recorte, rosto, camadas, gerador). Igual pra todos | nunca muda por estilo; melhorias valem pra todos os padrões |
| `padroes/<nome>/` | **O visual.** `PLAYBOOK.md` (regras e porquês), `padrao.json` (valores que o motor lê), `CHANGELOG.md`, `fontes/`, `referencias/`, `analise/` | estilos |
| `marcas/<nome>/` | **O criador.** `marca.json`, logos claro/escuro, `glossario.md`, LUT do cenário (`cor/`), `meus-editados/` | pessoas/clientes |
| `projetos/<slug>/` | **Um vídeo.** `projeto.json` (padrão, marca, aceleração, grading), `edicao.json` (o que entra e quando), `cortes.json`, `plano.md`, `insercoes/`, `composicao/` | vídeos |

Regras:
- **Nunca** escrever valor visual fixo no motor: ele lê `padrao.json`. Recurso novo pedido por um padrão → implementar no motor de forma configurável, com o valor do padrão em `padrao.json`, e ligar/desligar em `"recursos"`.
- Correção da usuária sobre o visual → `padroes/<nome>/PLAYBOOK.md` + `padrao.json` + entrada no `CHANGELOG.md` do padrão. Sobre grafia de termos → `marcas/<nome>/glossario.md`.
- Ao mexer no motor, regenerar um projeto já aprovado (ex.: `taste-washing-5`) e comparar com snapshots anteriores: o resultado de um padrão aprovado não pode mudar sem pedido.
- Padrões existentes: `amanda` (v1.0, oficial, uso próprio). `topo-livre` (em criação, para clientes: fonte TikTok Sans, sem fonte paga nem logo fixo).

## Primeiro uso / padrão novo

Se o padrão pedido não tem `PLAYBOOK.md`, ou a usuária pede um padrão novo: guiar pela seção "Criar um padrão novo" do `LEIA-ME.md` (caminho A: partir de vídeos editados da marca; caminho B: copiar referências). Não editar um bruto sem padrão definido, a menos que ela peça explicitamente.

## Criação e atualização de um padrão (análise de referências)

Papéis das entradas:
- `marcas/<nome>/meus-editados/`: a base no caminho A. O padrão parte da identidade atual; as referências nunca a substituem.
- `padroes/<nome>/referencias/`: fonte de elementos isolados. Nunca copiar uma referência inteira; levar em conta o que a usuária disse que gosta em cada uma.
- Par editado + bruto do mesmo vídeo (`<nome>` e `<nome>-bruto`): comparar os dois pra inferir as regras de corte reais. É a evidência mais confiável.

Caminho B ("referência como base"): uma referência principal vira a base. Pedir 2 a 3 vídeos do mesmo criador e só tratar como estilo o que se repete entre eles. Replicar o estilo de edição, mas não a identidade do criador (logo, paleta exata, assinaturas visuais, bordões). Checar a licença das fontes (padrão para clientes: só fontes livres, ex. Google Fonts). Marcar o que depende da gravação (enquadramento, headroom, luz, fundo). Tabela "Referência principal | Proposta".

Método por vídeo: `ffprobe` → transcrição com tempo por palavra → silêncios (`silencedetect`) e cortes de cena → quadros nos cortes e em amostragem regular → medidas: pausa entre frases, cortes/min, legenda (posição, tamanho, palavras por tela, cor, contorno, animação), zooms, inserções (frequência, formato, bordas), efeitos de fundo, gancho (0–3 s), música/sfx, duração. Pra medir lógica de destaques de cor, detectar a cor automaticamente quadro a quadro (como foi feito com o vermelho do Kaio) e cruzar com a transcrição.

Entregável: tabela comparativa com valores numéricos; a usuária decide a coluna Proposta; só depois escrever `PLAYBOOK.md` + `padrao.json`. Deixar explícito o que foi medido e o que foi estimado. Apagar os quadros extraídos ao terminar.

## Nada cobre o rosto (PLAYBOOK §0, vale pra todo padrão)

Nunca posicionar título, cards, legendas ou palavras-chave em posições fixas. Rodar `motor/rosto.py` depois do recorte; o `motor/gerar.py` usa esse mapa (com zoom e deslocamento do fundo mesclado) pra colocar cada elemento abaixo do queixo; se não couber, o card encolhe; o rosto nunca cede. Conferir nos snapshots antes do preview.

## Cor e iluminação (PLAYBOOK 1.1)

Em todo vídeo, **antes de montar o plano**, perguntar qual grading usar: (1) o da marca (`marcas/<nome>/cor/*.cube`, padrão), (2) o de outra referência indicada, ou (3) manter o original. Mostrar comparação lado a lado (bruto | com grading | referência). Grava a escolha em `projeto.json` → `"grading"`. Aplicado no A-roll (`motor/cortes.py`) antes do recorte; inserções mantêm as cores originais.

Gerar LUT: `motor/grading.py --bruto <bruto> --ref <video>:<t1,t2,...> ... --saida marcas/<nome>/cor/<nome>.cube --comparar <jpg>`.
- Tempos de referência **só da pessoa falando**: montar uma grade dos quadros e conferir antes (b-roll e cards contaminam).
- A medição usa só **pele do rosto + fundo da sala** (máscara do recorte); a roupa não entra.
- A LUT da marca `amanda` já existe (`marcas/amanda/cor/meus-editados.cube`, 2026-10-12): reaproveitar.

## Fluxo obrigatório de cada edição (nunca pular etapas)

1. **Plano antes de editar.** Transcrever e apresentar o plano: cortes com timecodes, aceleração, duração final, legendas, zooms, inserções (tabela PLAYBOOK 4.0), efeitos, regras do padrão aplicadas, grading. Esperar a aprovação.
2. **Preview antes de renderizar.** `npx hyperframes preview` em `projetos/<slug>/composicao` e abrir no navegador do app. Ajustar por lá; conferir pontos com snapshots.
3. **Render só com aprovação explícita.** `npx hyperframes render -q delivery -o ../../../saida/<data>-<slug>-padrao-<nome>.mp4`. Conferir quadros do MP4 final.
4. **Registrar o aprendizado** no padrão (PLAYBOOK + padrao.json + CHANGELOG) ou na marca (glossário).

## Regras que valem em toda edição

- **Glossário da marca:** `motor/transcrever.py` passa os termos como contexto do Whisper. Aplicar a tabela de erros conhecidos pelo contexto ("cloud" só vira "Claude" quando o assunto é a IA). Termo novo ou duvidoso → perguntar e acrescentar.
- **Confirmação das inserções (PLAYBOOK 4.0):** tabela fala exata → entra/sai → duração → arquivo → tipo e posição, de todas as inserções. Gancho (~5 s) é pergunta separada: quantas inserções, tipo, posição, duração.
- **Recursos opcionais** (fundo mesclado, palavras-chave, efeito negativo, texto atrás): nunca aplicar sem pedido ou aprovação explícita, e só se o padrão os tiver em `"recursos"`.

## Lições técnicas

- **iCloud:** a Área de Trabalho sincroniza com o iCloud; ler o mesmo vídeo em dois processos dá "Operation timed out". Copiar o bruto pro scratchpad antes de processar.
- **Cortes:** os tempos globais do Whisper derivam até ~1 s. Rodar `motor/refinar_cortes.py` (retranscreve janelas curtas) e **sempre** validar com `motor/energia.py` (bordas e interior no nível do ruído da sala; `--perfil de ate` mostra os vales).
- **Conferência:** depois do A-roll, retranscrever o arquivo inteiro e comparar com o roteiro. Janelas curtas (<5 s) fazem o Whisper inventar palavras. Nas legendas, usar o texto do roteiro.
- **Corte duvidoso:** sílabas emendadas → não adivinhar. Gerar 2–3 versões curtas do trecho (`SendUserFile`) e deixar a usuária escolher pelo ouvido.
- **Uma cópia só da pessoa:** recorte nunca como segunda `<video>` no HyperFrames (dessincroniza no preview → "fantasma"). `motor/compor_camadas.py` embute fundo mesclado + texto atrás + recorte num vídeo único.
- **Ordem de dependência:** mudou corte, aceleração ou grading → `cortes.py`, recorte, `rosto.py`, `compor_camadas.py`, `gerar.py`. Mudou fundo mesclado/texto atrás → `compor_camadas.py` + `gerar.py`. Mudou legenda, palavra-chave, card, título ou valor do padrão (exceto fundo mesclado/texto atrás) → só `gerar.py`.
- **MediaPipe 1.1** não tem `mp.solutions`: a detecção de rosto do `/shorts` (claude-shorts) está quebrada. O motor usa `rosto.py` (pele dentro da máscara do recorte).

## Pesquisa de imagens e notícias (opcional, PLAYBOOK §5)

Só quando a usuária pedir: 1) propor 4–8 queries curtas e **esperar aprovação**; 2) buscar e montar galeria/lista numerada; 3) baixar só o escolhido, dizendo a origem, em `projetos/<slug>/insercoes/`; 4) se falhar, nunca travar o plano: dizer o que falhou e pedir o arquivo em `insercoes/` ("aguardando arquivo").

## Organização e restrições

- Bruto novo em `entrada/brutos/` → criar `projetos/<slug>/` (slug: minúsculas, sem acentos/espaços/colchetes) com `insercoes/` e `projeto.json`, e avisar a usuária.
- Não alterar `entrada/`, `marcas/*/meus-editados/` nem `padroes/*/referencias/`; trabalhar sobre cópias.
- Pouco espaço em disco: apagar intermediários (quadros, matte antigo, renders de teste) quando não forem mais necessários. Avisar antes de downloads grandes.
- Git: usar `/opt/homebrew/bin/git` (o `/usr/bin/git` exige Xcode CLT). Este projeto é **privado**: tem repositório próprio e é ignorado pelo repositório público do portfólio (`../.gitignore`). Nunca publicar sem pedido.
